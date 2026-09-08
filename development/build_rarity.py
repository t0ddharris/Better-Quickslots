"""Build v0.2: inventory-only quickslot rarity fill, preserving original outlines."""
import copy
import json
from pathlib import Path
import build_patch as base

ROOT = Path(__file__).resolve().parent
OLD = 'WBP_HUD_Quickslots_Button'
NEW = 'WBP_Inventory_QuickslotRarity'
BUTTON_DIR = ROOT / 'extracted/Dawnwalker/Content/_Dawnwalker/UI/_Unified/HUD/Quickslots'
INV_DIR = ROOT / 'extracted/Dawnwalker/Content/_Dawnwalker/UI/_Unified/GameHub/Inventory'
b = json.loads((ROOT / 'decoded/button.json').read_text(encoding='utf-8-sig'))
f = json.loads((ROOT / 'decoded/fill.json').read_text(encoding='utf-8-sig'))

def rename(x):
    if isinstance(x, str): return x.replace(OLD, NEW)
    if isinstance(x, list): return [rename(v) for v in x]
    if isinstance(x, dict): return {k: rename(v) for k, v in x.items()}
    return x

b = rename(b)
ex = base.expr
ptr = base.ptr
var = base.var

def sz(e):
    k = e['$type'].split('EX_')[1].split(',')[0]
    if k in ('InstanceVariable', 'LocalVariable', 'ObjectConst'): return 9
    if k in ('Nothing', 'EndOfScript', 'Self', 'True', 'False', 'IntZero'): return 1
    if k == 'Return': return 1 + sz(e['ReturnExpression'])
    if k == 'DynamicCast': return 9 + sz(e['Target'])
    if k == 'Context': return 13 + sz(e['ObjectExpression']) + sz(e['ContextExpression'])
    if k in ('LocalVirtualFunction', 'VirtualFunction'): return 14 + sum(map(sz, e['Parameters']))
    if k in ('FinalFunction', 'CallMath', 'LocalFinalFunction'): return 10 + sum(map(sz, e['Parameters']))
    if k == 'StructMemberContext': return 9 + sz(e['StructExpression'])
    if k == 'Let': return 9 + sz(e['Variable']) + sz(e['Expression'])
    if k == 'JumpIfNot': return 5 + sz(e['BooleanExpression'])
    if k == 'ByteConst': return 2
    if k == 'IntConst': return 5
    if k == 'StructConst': return 14 + sum(map(sz, e['Value']))
    raise ValueError(k)

def ctx(obj, inner, result=None):
    return ex('Context', ObjectExpression=obj, Offset=sz(inner), PropertyType=0,
              RValuePointer=result or ptr(), ContextExpression=inner)

def get_exp(asset, name):
    return next(e for e in asset['Exports'] if e['ObjectName'] == name)

def imp(asset, name):
    return -1-next(i for i,e in enumerate(asset['Imports']) if e['ObjectName']==name)

def add_import(name, outer, cp='/Script/CoreUObject', cn='Object'):
    for i,e in enumerate(b['Imports']):
        if e['ObjectName']==name and e['OuterIndex']==outer: return -1-i
    b['Imports'].append({'$type':'UAssetAPI.Import, UAssetAPI','ObjectName':name,
                        'OuterIndex':outer,'ClassPackage':cp,'ClassName':cn,
                        'PackageName':None,'bImportOptional':False})
    return -len(b['Imports'])

def prop(name, value, kind='Objects.ObjectPropertyData', **kw):
    return {'$type':f'UAssetAPI.PropertyTypes.{kind}, UAssetAPI', 'Name':name,
            'ArrayIndex':0,'PropertyGuid':None,'IsZero':False,'PropertyTagFlags':'None',
            'PropertyTypeName':None,'PropertyTagExtensions':'NoExtension','Value':value,**kw}

def struct(name, kind, value):
    return prop(name,value,'Structs.StructPropertyData', StructType=kind,SerializeNone=True,
                StructGUID='{00000000-0000-0000-0000-000000000000}',SerializationControl='NoExtension',Operation='None')

def vector(name,x,y):
    return struct(name,'Vector2D',[prop(name,{'$type':'UAssetAPI.UnrealTypes.FVector2D, UAssetAPI','X':x,'Y':y},'Structs.Vector2DPropertyData')])

cls = get_exp(b,NEW+'_C')
owner = b['Exports'].index(cls)+1
widget = imp(b,'Widget') if any(i['ObjectName']=='Widget' for i in b['Imports']) else add_import('Widget',imp(b,'/Script/UMG'),cn='Class')
panel = add_import('PanelWidget',imp(b,'/Script/UMG'),cn='Class')
get_parent = add_import('GetParent',widget)
get_child = add_import('GetChildAt',panel)
set_visibility = add_import('SetVisibility',widget)
get_rarity = add_import('GetRarityData',imp(b,'InventorySubsystem'))
rarity_row = add_import('ItemRarityRow',imp(b,'/Script/DogwoodInventory'))
image_class = imp(b,'Image')

# Use the existing authored diamond brush in expanding translucent layers.
# Unlike the old resource-free fill, each layer has a known renderable sprite.
background = get_exp(b,'Background')
fill = copy.deepcopy(background)
fill_idx = len(b['Exports'])+1
slot_idx = fill_idx+1
fill.update(ObjectName='QSH_RarityFill', SerialSize=0, SerialOffset=0)
brush = copy.deepcopy(next(p for p in background['Data'] if p['Name']=='Brush'))
# Brighten only the added outlines; runtime item rarity still supplies the hue.
def descendants(value):
    if isinstance(value,dict):
        yield value
        for child in value.values(): yield from descendants(child)
    elif isinstance(value,list):
        for child in value: yield from descendants(child)
tint_brush=copy.deepcopy(next(p for p in descendants(f) if p.get('StructType')=='SlateColor' and any(c.get('Name')=='SpecifiedColor' for c in p.get('Value',[]))))
tint_brush['Name']='TintColor'
for component in descendants(tint_brush):
    if all(channel in component for channel in ('R','G','B','A')):
        component.update(R=2.5,G=2.5,B=2.5,A=1.0)
brush['Value'].append(tint_brush)
fill['Data'] = [brush, prop('Slot',slot_idx),
    prop('Visibility','HitTestInvisible','Objects.EnumPropertyData',EnumType='ESlateVisibility',InnerType='ByteProperty'),
    prop('RenderOpacity',0.0,'Objects.FloatPropertyData'),
    struct('RenderTransform','WidgetTransform',[
        vector('Translation',0.0,0.0),vector('Scale',1.35,1.35),vector('Shear',0.0,0.0),
        prop('Angle',0.0,'Objects.FloatPropertyData')]),
    vector('RenderTransformPivot',0.5,0.5),
    prop('bIsVariable',False,'Objects.BoolPropertyData')]
fill['CreateBeforeSerializationDependencies'] = [slot_idx]
old_slot = b['Exports'][next(p['Value'] for p in background['Data'] if p['Name']=='Slot')-1]
slot = copy.deepcopy(old_slot)
slot.update(ObjectName='QSH_RarityFillSlot',SerialSize=0,SerialOffset=0)
for p in slot['Data']:
    if p['Name']=='Content': p['Value']=fill_idx
slot['CreateBeforeSerializationDependencies']=[fill_idx]
parent_idx = next(p['Value'] for p in slot['Data'] if p['Name']=='Parent')
parent = b['Exports'][parent_idx-1]
slots = next(p for p in parent['Data'] if p['Name']=='Slots')['Value']
slots.insert(0, prop('0',slot_idx))
for i,p in enumerate(slots): p['Name']=str(i)
parent['CreateBeforeSerializationDependencies'].append(slot_idx)
b['Exports'].extend([fill,slot])

# Five closely spaced outlines produce a gentle falloff behind the original.
glow_opacities=[0.35,0.50,0.68,0.85,1.0]
for layer,scale in enumerate([1.31,1.27,1.23,1.19],start=1):
    layer_idx=len(b['Exports'])+1
    layer_slot_idx=layer_idx+1
    layer_fill=copy.deepcopy(fill)
    layer_fill.update(ObjectName=f'QSH_RarityGlowLayer{layer}',CreateBeforeSerializationDependencies=[layer_slot_idx])
    for p in layer_fill['Data']:
        if p['Name']=='Slot': p['Value']=layer_slot_idx
        if p['Name']=='RenderTransform':
            next(v for v in p['Value'] if v['Name']=='Scale')['Value'][0]['Value'].update(X=scale,Y=scale)
    layer_slot=copy.deepcopy(slot)
    layer_slot.update(ObjectName=f'QSH_RarityGlowSlotLayer{layer}',CreateBeforeSerializationDependencies=[layer_idx])
    next(p for p in layer_slot['Data'] if p['Name']=='Content')['Value']=layer_idx
    slots.insert(layer,prop(str(layer),layer_slot_idx))
    parent['CreateBeforeSerializationDependencies'].append(layer_slot_idx)
    b['Exports'].extend([layer_fill,layer_slot])
for i,p in enumerate(slots): p['Name']=str(i)

# Resolve the new first child through the existing ItemBox parent. No new
# class property is required and no shared HUD instance is altered.
glow_names=['QSH_RarityFill']+[f'QSH_RarityGlowLayer{i}' for i in range(1,5)]
icon_property=next(p for p in cls['LoadedProperties'] if p['Name']=='ItemIcon')
for name in glow_names:
    member=copy.deepcopy(icon_property)
    member['Name']=name
    cls['LoadedProperties'].append(member)
    image=get_exp(b,name)
    next(p for p in image['Data'] if p['Name']=='bIsVariable')['Value']=True
def glow_expr(layer):
    return var(glow_names[layer],owner)
set_opacity = add_import('SetRenderOpacity',widget)
def opacity(value,layer):
    return ctx(glow_expr(layer),ex('FinalFunction',StackNode=set_opacity,Parameters=[ex('FloatConst',Value=value)]))

# Extend size support only for the float argument used in SetRenderOpacity.
old_sz = sz
def sz(e):
    if e['$type'].split('EX_')[1].split(',')[0]=='FloatConst': return 5
    return old_sz(e)

item_asset=var('Displayed Item Asset',owner)
rarity=ctx(item_asset,var('ItemRarity',imp(b,'ItemBaseDataAsset')),ptr('ItemRarity',imp(b,'ItemBaseDataAsset')))
subsystem=ex('CallMath',StackNode=imp(b,'GetGameInstanceSubsystem'),Parameters=[ex('Self'),ex('ObjectConst',Value=imp(b,'InventorySubsystem'))])
fn_idx=len(b['Exports'])+1
row_pointer=ptr('QSH_RarityData',fn_idx)
row_variable=var('QSH_RarityData',fn_idx,True)
row=ctx(subsystem,ex('FinalFunction',StackNode=get_rarity,Parameters=[rarity]),row_pointer)
# EX_StructMemberContext evaluates its input for an address, with no result
# buffer. A native struct-returning call cannot safely be that input. Store
# the complete return value first, as the original WBP_OverlayFill does.
store_row=ex('Let',Value=row_pointer,Variable=row_variable,Expression=row)
color=ex('StructMemberContext',StructMemberExpression=ptr('RarityOverlayColor',rarity_row),StructExpression=row_variable)
# The authored warm border texture mutes the game's pale blue overlay color.
# Saturate blue-rarity outlines only, selected by item rarity rather than slot.
blue=ex('StructConst',Struct=imp(b,'LinearColor'),StructSize=16,
        Value=[ex('FloatConst',Value=v) for v in (0.025,0.12,0.9,1.0)])
is_blue=ex('CallMath',StackNode=add_import('EqualEqual_ByteByte',imp(b,'KismetMathLibrary')),
           Parameters=[rarity,ex('ByteConst',Value=4)])
color=ex('CallMath',StackNode=imp(b,'SelectColor'),Parameters=[blue,color,is_blue])
def tint(layer):
    return ctx(glow_expr(layer),ex('FinalFunction',StackNode=imp(b,'SetColorAndOpacity'),Parameters=[color]))
is_valid=ex('CallMath',StackNode=imp(b,'IsValid'),Parameters=[item_asset])
ret=[ex('Return',ReturnExpression=ex('Nothing')),ex('EndOfScript')]
body=[opacity(0.0,i) for i in range(5)]
body.extend([ex('JumpIfNot',CodeOffset=0,BooleanExpression=is_valid),store_row])
for i,alpha in enumerate(glow_opacities): body.extend([tint(i),opacity(alpha,i)])
body[5]['CodeOffset']=sum(map(sz,body))
fn=copy.deepcopy(get_exp(b,'Construct'))
row_property=copy.deepcopy(next(p for p in f['Exports'][0]['LoadedProperties'] if p['Name']=='CallFunc_GetRarityData_ReturnValue'))
row_property.update(Name='QSH_RarityData',Struct=rarity_row,PropertyFlags='CPF_None')
fn.update(ObjectName='QSH_UpdateRarity',FunctionFlags='FUNC_Public, FUNC_HasDefaults, FUNC_BlueprintCallable',
          SuperStruct=0,SuperIndex=0,LoadedProperties=[row_property],ScriptBytecode=body+ret,
          ScriptBytecodeSize=sum(map(sz,body+ret)),SerialSize=0,SerialOffset=0,
          SerializationBeforeSerializationDependencies=[],CreateBeforeSerializationDependencies=[])
b['Exports'].append(fn)
cls['FuncMap'].append(['QSH_UpdateRarity',fn_idx])
cls['Children'].append(fn_idx)
cls['CreateBeforeSerializationDependencies'].append(fn_idx)

# Every return from Update Displayed Item passes through the new function.
# Existing flow/jump offsets point to the same return boundary, now the call.
update=get_exp(b,'Update Displayed Item')
assert update['ScriptBytecode'][-2:]==ret
call=ex('LocalVirtualFunction',VirtualFunctionName='QSH_UpdateRarity',Parameters=[])
update['ScriptBytecode'].insert(len(update['ScriptBytecode'])-2,call)
update['ScriptBytecodeSize']+=sz(call)

def collect_names(asset):
    # Append potential new FNames; harmless extra names are retained to make
    # both serialization and Zen conversion deterministic.
    names=asset['NameMap']
    def walk(x):
        if isinstance(x,dict):
            for k,v in x.items():
                if k in ('Name','ObjectName','VirtualFunctionName','StructType','EnumType','InnerType','ClassName','ClassPackage') and isinstance(v,str) and v not in names: names.append(v)
                if k=='Path' and isinstance(v,list):
                    for n in v:
                        if n not in names: names.append(n)
                if k=='Value' and isinstance(v,str) and '$type' in x and 'EnumPropertyData' in x['$type'] and v not in names: names.append(v)
                walk(v)
        elif isinstance(x,list):
            for v in list(x): walk(v)
    walk(asset['Exports']); walk(asset['Imports'])
    asset['NamesReferencedFromExportDataCount']=len(names)

collect_names(b)
(BUTTON_DIR/'rarity-button.json').write_text(json.dumps(b,indent=2),encoding='utf-8')

q=json.loads((ROOT/'decoded/quickslots.json').read_text(encoding='utf-8-sig'))
q=rename(q)
q=json.loads(json.dumps(q).replace('WBP_Inventory_Quickslots','WBP_Inventory_Quickslots_QSH'))
collect_names(q)
(INV_DIR/'rarity-quickslots.json').write_text(json.dumps(q,indent=2),encoding='utf-8')

# Existing hover must cast to the new inventory-specific button class.
h=json.loads(base.OUTPUT.read_text(encoding='utf-8'))
h=rename(h)
# Redirect only class/package references; retain the existing widget member name.
def inventory_reference(x):
    if isinstance(x,str):
        if '/WBP_Inventory_Quickslots' in x or x in ('WBP_Inventory_Quickslots_C','Default__WBP_Inventory_Quickslots_C'):
            return x.replace('WBP_Inventory_Quickslots','WBP_Inventory_Quickslots_QSH')
        return x
    if isinstance(x,list): return [inventory_reference(v) for v in x]
    if isinstance(x,dict): return {k:inventory_reference(v) for k,v in x.items()}
    return x
h=inventory_reference(h)
collect_names(h)
(INV_DIR/'rarity-hub.json').write_text(json.dumps(h,indent=2),encoding='utf-8')
print('Built rarity sources: cloned inventory button, inventory quickslots, hover-compatible hub.')
