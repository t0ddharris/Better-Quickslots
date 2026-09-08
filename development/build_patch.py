"""Patch only the inventory screen; preserve the shared HUD button asset."""
import copy
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / 'decoded/hub.json'
OUTPUT = ROOT / 'extracted/Dawnwalker/Content/_Dawnwalker/UI/_Unified/GameHub/Inventory/hover-patched.json'
a = json.loads(SOURCE.read_text(encoding='utf-8-sig'))
exports = a['Exports']

def export(name):
    return next(e for e in exports if e['ObjectName'] == name)

def imp(name):
    return -1 - next(i for i, e in enumerate(a['Imports']) if e['ObjectName'] == name)

def expr(kind, **fields):
    return {'$type': f'UAssetAPI.Kismet.Bytecode.Expressions.EX_{kind}, UAssetAPI', **fields}

def ptr(name=None, owner=0):
    return {'$type': 'UAssetAPI.Kismet.Bytecode.KismetPropertyPointer, UAssetAPI',
            'New': {'$type': 'UAssetAPI.UnrealTypes.FFieldPath, UAssetAPI',
                    'Path': [] if name is None else [name], 'ResolvedOwner': owner}}

def var(name, owner, local=False):
    return expr('LocalVariable' if local else 'InstanceVariable', Variable=ptr(name, owner))

def size(e):
    k = e['$type'].split('EX_')[1].split(',')[0]
    if k in ('InstanceVariable', 'LocalVariable'): return 9
    if k in ('Nothing', 'EndOfScript', 'Self'): return 1
    if k == 'Return': return 1 + size(e['ReturnExpression'])
    if k == 'DynamicCast': return 9 + size(e['Target'])
    if k == 'Context': return 13 + size(e['ObjectExpression']) + size(e['ContextExpression'])
    if k == 'LocalVirtualFunction': return 14 + sum(map(size, e['Parameters']))
    if k == 'LocalFinalFunction': return 10 + sum(map(size, e['Parameters']))
    if k == 'IntConst': return 5
    if k == 'InstanceDelegate': return 13
    if k == 'AddMulticastDelegate': return 1 + size(e['Delegate']) + size(e['DelegateToAdd'])
    if k == 'StructConst': return 14 + sum(map(size, e['Value']))
    raise ValueError(k)

def context(obj, inner, result=None):
    return expr('Context', ObjectExpression=obj, Offset=size(inner), PropertyType=0,
                RValuePointer=ptr() if result is None else result, ContextExpression=inner)

cls = export('WBP_Hub_NewInventory_C')
owner = exports.index(cls) + 1
quick_owner = imp('WBP_Inventory_Quickslots_C')
common = imp('CommonButtonBase')

# Add a reference, not a replacement, to the existing quickslot button class.
pkg = '/Game/_Dawnwalker/UI/_Unified/HUD/Quickslots/WBP_HUD_Quickslots_Button'
for name, outer, cp, cn in [(pkg, 0, '/Script/CoreUObject', 'Package'),
                           ('WBP_HUD_Quickslots_Button_C', -len(a['Imports'])-1,
                            '/Script/UMG', 'WidgetBlueprintGeneratedClass')]:
    a['Imports'].append({'$type': 'UAssetAPI.Import, UAssetAPI', 'ObjectName': name,
                         'OuterIndex': outer, 'ClassPackage': cp, 'ClassName': cn,
                         'PackageName': None, 'bImportOptional': False})
button_owner = imp('WBP_HUD_Quickslots_Button_C')

def panel_call(item):
    return context(var('WBP_InventoryPanel', owner),
                   expr('LocalVirtualFunction', VirtualFunctionName='Set External Focused Item', Parameters=[item]))

empty = expr('StructConst', Struct=imp('ItemHandle'), StructSize=4, Value=[])
clear = panel_call(empty)
template = export('OnInitialized')
param_template = export('BndEvt__WBP_NewInventory_ActionButton_K2Node_ComponentBoundEvent_3_CommonButtonBaseClicked__DelegateSignature')['LoadedProperties']

def add_function(name, body, with_button=True):
    fn = copy.deepcopy(template)
    idx = len(exports) + 1
    fn.update(ObjectName=name, FunctionFlags='FUNC_Public, FUNC_BlueprintCallable',
              SuperStruct=0, SuperIndex=0,
              LoadedProperties=copy.deepcopy(param_template) if with_button else [],
              ScriptBytecode=body + [expr('Return', ReturnExpression=expr('Nothing')), expr('EndOfScript')],
              SerializationBeforeSerializationDependencies=[],
              CreateBeforeSerializationDependencies=[], SerialSize=0, SerialOffset=0)
    fn['ScriptBytecodeSize'] = sum(map(size, fn['ScriptBytecode']))
    exports.append(fn)
    cls['FuncMap'].append([name, idx])
    cls['Children'].append(idx)
    cls['CreateBeforeSerializationDependencies'].append(idx)
    return idx

hover_name, leave_name = 'QSH_InventoryHover', 'QSH_InventoryUnhover'
hover_idx = len(exports) + 1
cast = expr('DynamicCast', ClassPtr=button_owner, Target=var('Button', hover_idx, True))
item = context(cast, var('Displayed Item', button_owner), ptr('Displayed Item', button_owner))
add_function(hover_name, [panel_call(item)])
add_function(leave_name, [clear])

bindings = []
for slot in ('Left', 'Top', 'Right', 'Bottom'):
    button = context(var('WBP_Inventory_Quickslots', owner), var(slot, quick_owner), ptr(slot, quick_owner))
    for event, handler in [('OnButtonBaseHovered', hover_name), ('OnButtonBaseUnhovered', leave_name)]:
        bindings.append(expr('AddMulticastDelegate',
            Delegate=context(button, var(event, common), ptr(event, common)),
            DelegateToAdd=expr('InstanceDelegate', FunctionName=handler)))

# Bind once per screen instance, after original initialization. Existing ubergraph offsets stay intact.
init = export('OnInitialized')
init['ScriptBytecode'][1:1] = bindings
init['ScriptBytecodeSize'] = sum(map(size, init['ScriptBytecode']))
# Closing the inventory also clears hover, even if Slate does not deliver pointer exit.
deactivate = export('BP_OnDeactivated')
deactivate['ScriptBytecode'].insert(0, clear)
deactivate['ScriptBytecodeSize'] = sum(map(size, deactivate['ScriptBytecode']))

# New serialized names must be present before UAssetAPI writes the name table.
for name in [pkg, 'WBP_HUD_Quickslots_Button_C', 'Displayed Item', hover_name, leave_name,
             'Left', 'Top', 'Right', 'Bottom', 'OnButtonBaseHovered', 'OnButtonBaseUnhovered']:
    if name not in a['NameMap']: a['NameMap'].append(name)
a['NamesReferencedFromExportDataCount'] = len(a['NameMap'])

assert all('RawExport' not in e['$type'] for e in exports)
assert len(bindings) == 8
OUTPUT.write_text(json.dumps(a, indent=2), encoding='utf-8')
print(f'Patched {OUTPUT.name}: 4 hover bindings, 4 unhover bindings, inventory-close cleanup.')
