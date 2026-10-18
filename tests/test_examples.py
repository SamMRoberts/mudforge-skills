"""Lua 5.1 logic fixtures, not a MudForge engine or native acceptance harness."""

from pathlib import Path
import re
import unittest

from lupa.lua51 import LuaRuntime, LuaError

PLUGIN = Path(__file__).resolve().parents[1] / "plugins/mudforge-toolbox"

HARNESS = r'''
fixture = {
  sequence=0, commands={}, commandRegistrations=0, triggers={}, aliases={}, timers={},
  outputs={}, vars={}, gmcp={}, msdp={}, events={}, widgets={}, widgetEvents={},
  bindings={}, contentWrites=0, subscriptionCount=0, connected=false, session="alpha",
  ready=false, rooms={}, mapReads=0, mapWrites=0, drawings={}, active=nil, widgetFont="21px Fixture",
  nearby={}, highlights={}, highlightWrites={}, visibilityWrites={}, destroyed={},
  mapReadyRegistrations=0, mapSubscriptions=0, timerRefused=false
}
local function id(prefix)
  fixture.sequence = fixture.sequence + 1
  return prefix .. tostring(fixture.sequence)
end
function echo(value) table.insert(fixture.outputs, value) end
function getSessionId() return fixture.session end
function getSession()
  if fixture.noSession then return nil end
  return {id=fixture.session,connected=fixture.connected}
end
function getVariable(key) return fixture.vars[key] end
function setVariable(key,value) fixture.vars[key]=tostring(value) end
function registerCommand(name,fn)
  fixture.commandRegistrations=fixture.commandRegistrations+1
  fixture.commands[name]=fn
end
function addTrigger(pattern,fn,options)
  local key=id("trigger")
  fixture.triggers[key]={pattern=pattern,callback=fn,options=options}
  return key
end
function removeTrigger(key) fixture.triggers[key]=nil end
function addAlias(pattern,replacement,fn,options)
  local key=id("alias")
  fixture.aliases[key]={pattern=pattern,callback=fn,replacement=replacement,options=options}
  return key
end
function removeAlias(key) fixture.aliases[key]=nil end
function addTimer(ms,fn,repeating)
  if not fixture.connected or fixture.timerRefused then return "" end
  local key=id("timer")
  fixture.timers[key]={ms=ms,callback=fn,repeating=repeating}
  return key
end
function removeTimer(key) fixture.timers[key]=nil end
function onGMCPUpdate(package,fn)
  fixture.subscriptionCount=fixture.subscriptionCount+1
  fixture.gmcp[package]=fn
end
function onMSDPChange(name,fn)
  fixture.subscriptionCount=fixture.subscriptionCount+1
  fixture.msdp[name]=fn
end
function emit(name,value) table.insert(fixture.events,{name=name,data=value}) end
function createWidget(config)
  local key=id("widget")
  fixture.widgets[key]=config
  if config.visible == nil then config.visible=true end
  fixture.widgetEvents[key]={}
  return key
end
function createMapperWidget(name,config)
  if fixture.mapperRefused then return nil end
  config.name=name
  config.type="map"
  return createWidget(config)
end
function getWidgetProperty(key,prop) return fixture.widgets[key][prop] end
function showWidget(key,force)
  fixture.widgets[key].visible=true
  table.insert(fixture.visibilityWrites,{key=key,visible=true,force=force})
end
function hideWidget(key,force)
  fixture.widgets[key].visible=false
  table.insert(fixture.visibilityWrites,{key=key,visible=false,force=force})
end
function setWidgetProperty(key,prop,value)
  fixture.widgets[key][prop]=value
  if prop=="content" then fixture.contentWrites=fixture.contentWrites+1 end
end
function setBoundValues(key,values) fixture.bindings[key]=values end
function registerWidgetEvent(key,event,fn) fixture.widgetEvents[key][event]=fn end
function destroyWidget(key)
  table.insert(fixture.destroyed,key)
  fixture.widgets[key]=nil
  fixture.widgetEvents[key]=nil
  fixture.bindings[key]=nil
end
function setActiveWidget(key) fixture.active=key end
function getWidgetFont(key) return {size=21,css=fixture.widgetFont} end
function measureText(text,font) return {width=#text*8} end
function getCanvasWidth()
  return fixture.canvasWidth or fixture.widgets[fixture.active].size.width
end
function getCanvasHeight()
  return fixture.canvasHeight or fixture.widgets[fixture.active].size.height
end
function drawCircle(x,y,r,fill,stroke)
  assert(type(x)=="number" and fixture.active, "incorrect drawing signature")
  table.insert(fixture.drawings,{kind="circle",active=fixture.active,x=x,y=y,r=r,fill=fill,stroke=stroke})
end
function drawLine(x1,y1,x2,y2,color,width)
  assert(type(x1)=="number" and fixture.active, "incorrect drawing signature")
  table.insert(fixture.drawings,{kind="line",active=fixture.active,x1=x1,y1=y1,x2=x2,y2=y2,color=color,width=width})
end
function clear(color) table.insert(fixture.drawings,{kind="clear",active=fixture.active,color=color}) end
function drawRect(x,y,w,h,color,stroke)
  assert(type(x)=="number" and fixture.active, "incorrect drawing signature")
  table.insert(fixture.drawings,{kind="rect",active=fixture.active,x=x,y=y,w=w,h=h,color=color,stroke=stroke})
end
function drawText(text,x,y,color,font)
  assert(type(x)=="number" and fixture.active, "incorrect drawing signature")
  table.insert(fixture.drawings,{kind="text",active=fixture.active,text=text,x=x,y=y,color=color,
    fontOverride=font,font=font or fixture.widgetFont})
end
function isMapReady() return fixture.ready end
function onMapReady(fn)
  fixture.mapReadyRegistrations=fixture.mapReadyRegistrations+1
  fixture.mapReadyCallback=fn
end
function onRoomChange(fn)
  fixture.mapSubscriptions=fixture.mapSubscriptions+1
  fixture.roomChangeCallback=fn
end
function onMapUpdate(fn)
  fixture.mapSubscriptions=fixture.mapSubscriptions+1
  fixture.mapUpdateCallback=fn
end
function onMapRoomClick(fn)
  fixture.mapSubscriptions=fixture.mapSubscriptions+1
  fixture.roomClickCallback=fn
end
function findRoomsWithin(room,range)
  fixture.nearbyRoom=room
  fixture.nearbyRange=range
  return fixture.nearby
end
function highlightRoom(room,color,options)
  if fixture.highlightRefused then return false end
  fixture.highlights[room]={color=color,opacity=options.opacity}
  table.insert(fixture.highlightWrites,{room=room,highlighted=true})
  return true
end
function unhighlightRoom(room)
  fixture.highlights[room]=nil
  table.insert(fixture.highlightWrites,{room=room,highlighted=false})
end
function getPlayerRoom()
  fixture.mapReads=fixture.mapReads+1
  return fixture.currentRoom
end
function getMapRoom(key)
  fixture.mapReads=fixture.mapReads+1
  return fixture.rooms[key]
end
function addMapRoom(key,fields)
  if fixture.rooms[key] then return false end
  fixture.mapWrites=fixture.mapWrites+1
  fixture.rooms[key]=fields
  return true
end
function setMapExit(from,dir,to)
  fixture.mapWrites=fixture.mapWrites+1
  local room=fixture.rooms[from]
  room.exits=room.exits or {}
  room.exits[dir]=to
  return true
end
'''


class Runtime:
    def __init__(self, name=None):
        self.lua = LuaRuntime(unpack_returned_tuples=True)
        self.lua.execute(HARNESS)
        self.g = self.lua.globals()
        self.f = self.g.fixture
        if name:
            self.lua.execute(next(PLUGIN.glob('skills/*/assets/'+name)).read_text())

    def table(self, **values):
        return self.lua.table_from(values)

    def command(self, name):
        return self.f.commands[name]("")

    def only(self, table):
        items = list(table.items())
        if len(items) != 1:
            raise AssertionError(f'expected one entry, found {len(items)}')
        return items[0]

    def library(self, name):
        source = next(PLUGIN.glob('skills/*/assets/'+name)).read_text()
        # A restricted library scope demonstrates explicit dependency injection.
        return self.lua.eval('''function(source)
          local environment={assert=assert,type=type,tostring=tostring,tonumber=tonumber,
            pairs=pairs,ipairs=ipairs,math=math,table=table,string=string}
          local fn=assert(loadstring(source))
          setfenv(fn,environment)
          return fn()
        end''')(source)


class ExampleTests(unittest.TestCase):
    def test_all_examples_parse_as_lua51(self):
        lua = LuaRuntime()
        parse = lua.eval('function(source) local fn,err=loadstring(source); return fn~=nil,err end')
        files = sorted(PLUGIN.glob('skills/*/assets/*.lua'))
        self.assertEqual(len(files), 10)
        for path in files:
            with self.subTest(example=path.name):
                ok, error = parse(path.read_text())
                self.assertTrue(ok, error)

    def test_trigger_and_alias_capture_contracts(self):
        runtime = Runtime('automation.lua')
        runtime.g.init()
        _, trigger = runtime.only(runtime.f.triggers)
        self.assertEqual(trigger.options.type, 'regex')
        match = re.fullmatch(trigger.pattern, 'Toolbox score: 42')
        self.assertIsNotNone(match)
        raw_captures = runtime.lua.table_from(dict(enumerate(match.groups())))
        wildcards = runtime.lua.table_from(dict(enumerate([match.group(0), *match.groups()])))
        self.assertIsNone(trigger.callback(raw_captures, match.group(0), wildcards, match.group(0)))
        self.assertEqual(runtime.f.vars.score, '42')
        self.assertIsNone(re.fullmatch(trigger.pattern, 'Toolbox score: unavailable'))
        _, alias = runtime.only(runtime.f.aliases)
        self.assertEqual(alias.replacement, '')
        match = re.fullmatch(alias.pattern, 'toolbox-score 17')
        alias.callback(runtime.lua.table_from([match.group(0), *match.groups()]))
        self.assertEqual(runtime.f.vars.score, '17')

    def test_trigger_reads_first_wildcard_with_multiple_raw_captures(self):
        runtime = Runtime('automation.lua')
        runtime.g.init()
        _, trigger = runtime.only(runtime.f.triggers)
        # Exercise the callback boundary with unequal groups, not a native matcher.
        raw_captures = runtime.lua.table_from({0: '42', 1: '900'})
        wildcards = runtime.lua.table_from({0: '42/900', 1: '42', 2: '900'})
        trigger.callback(raw_captures, '42/900', wildcards, '42/900')
        self.assertEqual(runtime.f.vars.score, '42')

    def test_idempotent_init_and_cleanup(self):
        runtime = Runtime('automation.lua')
        runtime.g.init()
        runtime.g.init()
        self.assertEqual(len(list(runtime.f.triggers)), 1)
        self.assertEqual(len(list(runtime.f.aliases)), 1)
        self.assertEqual(runtime.f.commandRegistrations, 2)
        runtime.g.cleanup()
        runtime.g.cleanup()
        self.assertEqual(list(runtime.f.triggers), [])
        self.assertEqual(list(runtime.f.aliases), [])

    def test_timer_refusal_replacement_cancel_and_disconnect(self):
        runtime = Runtime('automation.lua')
        runtime.g.init()
        runtime.command('toolbox-delay')
        self.assertEqual(list(runtime.f.timers), [])
        self.assertIn('unavailable', runtime.f.outputs[1])
        runtime.f.connected = True
        runtime.command('toolbox-delay')
        first, timer = runtime.only(runtime.f.timers)
        self.assertEqual(timer.ms, 1000)
        self.assertFalse(timer.repeating)
        runtime.command('toolbox-delay')
        second, _ = runtime.only(runtime.f.timers)
        self.assertNotEqual(first, second)
        runtime.g.onDisconnect('other-session')
        self.assertEqual(len(list(runtime.f.timers)), 1)
        runtime.g.onDisconnect('alpha')
        self.assertEqual(list(runtime.f.timers), [])
        runtime.command('toolbox-delay')
        runtime.command('toolbox-cancel')
        self.assertEqual(list(runtime.f.timers), [])
        runtime.command('toolbox-delay')
        runtime.g.cleanup()
        self.assertEqual(list(runtime.f.timers), [])

    def test_counter_serialized_reload_contract(self):
        first = Runtime('lifecycle.lua')
        first.g.init()
        first.g.init()
        first.command('toolbox-count')
        first.command('toolbox-count')
        saved = dict(first.f.vars.items())
        second = Runtime('lifecycle.lua')
        second.f.vars = second.lua.table_from(saved)
        second.g.init()
        second.command('toolbox-count')
        self.assertEqual(second.f.vars.count, '3')
        self.assertEqual(first.f.commandRegistrations, 2)

    def test_library_injection_and_instance_isolation(self):
        first, second = Runtime(), Runtime()
        lib1 = first.library('injected-counter.lua')
        lib2 = second.library('injected-counter.lua')
        with self.assertRaises(LuaError):
            lib1.tick()
        lib1.init(first.table(echo=first.g.echo))
        lib2.init(second.table(echo=second.g.echo))
        self.assertEqual(lib1.tick(), 1)
        self.assertEqual(lib1.tick(), 2)
        self.assertEqual(lib2.tick(), 1)
        self.assertEqual(len(list(first.f.outputs)), 2)

    def test_protocol_partial_invalid_disconnect_and_two_sessions(self):
        first, second = Runtime('session-vitals.lua'), Runtime('session-vitals.lua')
        second.f.session = 'beta'
        for runtime in (first, second):
            runtime.g.init()
            runtime.g.init()
            self.assertEqual(runtime.f.subscriptionCount, 3)
        first.f.gmcp['Char.Vitals'](first.table(hp='40', maxhp='100'))
        first.f.gmcp['Char.Vitals'](first.table(hp='25'))
        self.assertEqual(first.f.events[2].data.maxhp, 100)
        self.assertEqual(first.f.events[2].data.hp, 25)
        second.f.msdp['HEALTH']('9', None)
        self.assertEqual(second.f.events[1].data.sessionId, 'beta')
        self.assertIsNone(second.f.events[1].data.maxhp)
        first.f.gmcp['Char.Vitals'](first.table(hp='invalid'))
        self.assertIsNone(first.f.events[3].data.hp)
        first.g.onDisconnect('beta')
        self.assertEqual(len(list(first.f.events)), 3)
        first.g.onDisconnect('alpha')
        first.f.gmcp['Char.Vitals'](first.table(hp='1'))
        self.assertIsNone(first.f.events[5].data.maxhp)

    def test_hud_keeps_markup_stable_and_binds_untrusted_text(self):
        runtime = Runtime('reactive-vitals.lua')
        runtime.g.init()
        runtime.g.init()
        widget, config = runtime.only(runtime.f.widgets)
        original = config.content
        self.assertEqual(runtime.f.contentWrites, 1)
        self.assertEqual(runtime.f.bindings[widget].hp, '?')
        runtime.f.gmcp['Char.Vitals'](runtime.table(hp='200', maxhp='100', label='<script>bad()</script>'))
        self.assertEqual(runtime.f.bindings[widget].percent, '100%')
        self.assertEqual(runtime.f.bindings[widget].label, '<script>bad()</script>')
        self.assertNotIn('<script>', config.content)
        runtime.f.gmcp['Char.Vitals'](runtime.table(hp='25'))
        self.assertEqual(runtime.f.bindings[widget].percent, '25%')
        self.assertEqual(config.content, original)
        runtime.f.gmcp['Char.Vitals'](runtime.table(maxhp='0'))
        self.assertEqual(runtime.f.bindings[widget].percent, '0%')
        self.assertEqual(runtime.f.bindings[widget].maximum, '?')
        self.assertEqual(runtime.f.bindings[widget].status, 'Waiting for valid vitals')
        runtime.f.gmcp['Char.Vitals'](runtime.table(maxhp='100'))
        self.assertEqual(runtime.f.bindings[widget].percent, '25%')
        self.assertEqual(runtime.f.bindings[widget].status, 'Ready')
        runtime.f.gmcp['Char.Vitals'](runtime.table(hp='not-a-number'))
        self.assertEqual(runtime.f.bindings[widget].hp, '?')
        runtime.f.widgetEvents[widget].action(runtime.table(action='reset'))
        self.assertEqual(runtime.f.bindings[widget].maximum, '?')
        runtime.command('toolbox-vitals-demo')
        runtime.g.onDisconnect('alpha')
        self.assertEqual(runtime.f.bindings[widget].hp, '?')
        runtime.g.cleanup()
        runtime.g.cleanup()
        self.assertEqual(list(runtime.f.widgets), [])
        # The runtime's textContent patch itself requires native verification.

    def test_vitals_reject_blank_before_host_numeric_coercion(self):
        for example in ('session-vitals.lua', 'reactive-vitals.lua'):
            with self.subTest(example=example):
                runtime = Runtime(example)
                # Inject one documented host quirk; this is not a transpiler emulator.
                runtime.lua.execute('''
                    local luaTonumber = tonumber
                    function tonumber(value)
                      if type(value) == "string" and value:match("^%s*$") then return 0 end
                      return luaTonumber(value)
                    end
                ''')
                runtime.g.init()
                update = runtime.f.gmcp['Char.Vitals']
                update(runtime.table(hp='25', maxhp='100'))
                for value in ('', '   '):
                    update(runtime.table(hp=value))
                    if example == 'session-vitals.lua':
                        event = runtime.f.events[len(list(runtime.f.events))]
                        self.assertIsNone(event.data.hp)
                        self.assertEqual(event.data.maxhp, 100)
                    else:
                        widget, _ = runtime.only(runtime.f.widgets)
                        self.assertEqual(runtime.f.bindings[widget].hp, '?')
                        self.assertEqual(runtime.f.bindings[widget].status, 'Waiting for valid vitals')

    def test_hud_ignores_missing_malformed_and_unrelated_actions(self):
        runtime = Runtime('reactive-vitals.lua')
        runtime.g.init()
        widget, _ = runtime.only(runtime.f.widgets)
        runtime.command('toolbox-vitals-demo')
        action = runtime.f.widgetEvents[widget].action
        for payload in (None, 'reset', runtime.table(), runtime.table(action='other')):
            action(payload)
            self.assertEqual(runtime.f.bindings[widget].hp, '25')
            self.assertEqual(runtime.f.bindings[widget].maximum, '100')
        action(runtime.table(action='reset'))
        self.assertEqual(runtime.f.bindings[widget].hp, '?')
        self.assertEqual(runtime.f.bindings[widget].maximum, '?')

    def test_canvas_selects_widget_and_reflows(self):
        runtime = Runtime('canvas-status.lua')
        runtime.g.init()
        widget, _ = runtime.only(runtime.f.widgets)
        self.assertEqual(runtime.f.drawings[2].w, 224)
        self.assertIsNone(runtime.f.drawings[3].fontOverride)
        self.assertEqual(runtime.f.drawings[3].font, '21px Fixture')
        runtime.f.widgetFont = '24px Changed'
        runtime.f.active = 'unrelated-widget'
        runtime.f.widgetEvents[widget].resize(runtime.table(width=320, height=120))
        self.assertEqual(runtime.f.drawings[5].active, widget)
        self.assertEqual(runtime.f.drawings[5].w, 304)
        self.assertEqual(runtime.f.drawings[5].h, 104)
        self.assertIsNone(runtime.f.drawings[6].fontOverride)
        self.assertEqual(runtime.f.drawings[6].font, '24px Changed')

    def test_mapper_preserves_existing_room_and_exit(self):
        runtime = Runtime()
        library = runtime.library('guarded-map.lua')
        library.init(runtime.table(isMapReady=runtime.g.isMapReady, getMapRoom=runtime.g.getMapRoom,
                                   addMapRoom=runtime.g.addMapRoom, setMapExit=runtime.g.setMapExit))
        room = runtime.table(name='One', area='Fixture')
        self.assertEqual(library.ensureRoom(1, room), 'not-ready')
        runtime.f.ready = True
        self.assertEqual(library.ensureRoom(1, room), 'created')
        self.assertEqual(library.ensureRoom(1, room), 'unchanged')
        self.assertEqual(library.ensureRoom(1, runtime.table(name='Different', area='Fixture')), 'room-conflict')
        library.ensureRoom(2, runtime.table(name='Two', area='Fixture'))
        library.ensureRoom(3, runtime.table(name='Three', area='Fixture'))
        self.assertEqual(library.ensureExit(1, 'n', 2), 'created')
        writes = runtime.f.mapWrites
        self.assertEqual(library.ensureExit(1, 'n', 3), 'exit-conflict')
        self.assertEqual(library.ensureExit(1, 'n', 2), 'unchanged')
        self.assertEqual(library.ensureExit(1, 's', 99), 'missing-room')
        self.assertEqual(library.ensureExit(1, 'enter portal', 3), 'invalid-exit')
        self.assertEqual(library.ensureRoom(-1, room), 'invalid-room')
        self.assertEqual(runtime.f.mapWrites, writes)
        self.assertEqual(runtime.f.rooms[1].exits.n, 2)

    def test_map_inspector_cold_and_missing_room(self):
        runtime = Runtime('map-inspector.lua')
        runtime.g.init()
        runtime.command('toolbox-map-inspect')
        self.assertEqual(runtime.f.outputs[1], 'Map is not ready.')
        runtime.f.ready = True
        runtime.command('toolbox-map-inspect')
        self.assertEqual(runtime.f.outputs[2], 'No current room reported.')
        self.assertEqual(runtime.f.mapWrites, 0)
        # Native JS-array iteration is deliberately not simulated by a Lua table.


class MinimapExampleTests(unittest.TestCase):
    """Observe Lua callback logic; fixtures do not emulate native drawing or map transport."""

    def ready_runtime(self, *, mapped=True):
        runtime = Runtime('mapper-minimap.lua')
        runtime.f.currentRoom = 10
        if mapped:
            runtime.f.rooms[10] = runtime.table(x=0, y=0, z=0, name='Origin')
        runtime.g.init()
        runtime.f.ready = True
        runtime.f.mapReadyCallback()
        return runtime

    def widget(self, runtime, name):
        matches = [(key, config) for key, config in runtime.f.widgets.items()
                   if config.name == name]
        self.assertEqual(len(matches), 1)
        return matches[0]

    def drawings(self, runtime, kind=None):
        drawings = [runtime.f.drawings[index]
                    for index in range(1, len(runtime.f.drawings) + 1)]
        return [drawing for drawing in drawings if kind is None or drawing.kind == kind]

    def alias(self, runtime):
        _, alias = runtime.only(runtime.f.aliases)
        self.assertEqual(alias.pattern, '^toolbox-radar$')
        self.assertEqual(alias.replacement, '')
        return alias.callback

    def test_minimap_waits_for_readiness_and_sets_up_once(self):
        runtime = Runtime('mapper-minimap.lua')
        runtime.g.init()
        runtime.g.init()
        self.assertEqual(runtime.f.mapReadyRegistrations, 1)
        self.assertEqual(list(runtime.f.widgets), [])
        self.assertEqual(list(runtime.f.timers), [])
        self.alias(runtime)(runtime.lua.table_from(['toolbox-radar']))
        self.assertEqual(runtime.f.mapReads, 0)
        runtime.f.ready = True
        runtime.f.mapReadyCallback()
        native_id, native = self.widget(runtime, 'minimap')
        radar_id, radar = self.widget(runtime, 'radar')
        self.assertNotEqual(native_id, radar_id)
        self.assertFalse(native.interactive)
        self.assertEqual((native.x, native.y), (24, 90))
        self.assertEqual((radar.position.x, radar.position.y), (320, 90))
        self.assertEqual(runtime.f.mapSubscriptions, 3)
        self.assertTrue(self.drawings(runtime))
        runtime.f.mapReadyCallback()
        runtime.g.init()
        self.assertEqual(len(list(runtime.f.widgets)), 2)
        self.assertEqual(runtime.f.mapSubscriptions, 3)
        self.assertEqual(len(list(runtime.f.aliases)), 1)
        self.assertEqual(list(runtime.f.timers), [])
        self.assertEqual(runtime.f.mapWrites, 0)

    def test_native_minimap_refusal_keeps_radar_usable(self):
        runtime = Runtime('mapper-minimap.lua')
        runtime.f.mapperRefused = True
        runtime.g.init()
        runtime.f.ready = True
        runtime.f.mapReadyCallback()
        radar_id, _ = self.widget(runtime, 'radar')
        self.assertEqual(len(list(runtime.f.widgets)), 1)
        self.assertTrue(any('unavailable' in value.lower()
                            for _, value in runtime.f.outputs.items()))
        self.assertTrue(self.drawings(runtime, 'text'))
        self.alias(runtime)(runtime.lua.table_from(['toolbox-radar']))
        self.assertFalse(runtime.f.widgets[radar_id].visible)
        runtime.g.cleanup()
        self.assertEqual(list(runtime.f.widgets), [])
        self.assertEqual(list(runtime.f.destroyed.values()), [radar_id])

    def test_radar_explains_waiting_and_unmapped_locations(self):
        runtime = self.ready_runtime(mapped=False)
        self.assertTrue(any("isn't mapped" in item.text
                            for item in self.drawings(runtime, 'text')))
        player = self.drawings(runtime)[-1]
        self.assertEqual((player.kind, player.x, player.y, player.r),
                         ('circle', 110, 110, 4))
        runtime.f.currentRoom = None
        runtime.f.drawings = runtime.lua.table()
        runtime.f.roomChangeCallback()
        messages = self.drawings(runtime, 'text')
        self.assertTrue(any('location' in item.text.lower() for item in messages))
        for item in messages:
            self.assertIsNone(item.fontOverride)
            self.assertEqual(item.font, '21px Fixture')
        for invalid in ('bad', float('nan'), float('inf'), 0):
            runtime.f.currentRoom = invalid
            runtime.f.roomChangeCallback()
            self.assertIn('location', self.drawings(runtime)[-1].text.lower())
        runtime.f.currentRoom = 10
        runtime.f.rooms[10] = runtime.table(x=0, y=0, z='bad')
        runtime.f.roomChangeCallback()
        self.assertTrue(any("isn't mapped" in item.text
                            for item in self.drawings(runtime, 'text')))
        runtime.f.ready = False
        runtime.f.mapUpdateCallback()
        self.assertIn('map', self.drawings(runtime)[-1].text.lower())

    def test_radar_normalizes_keys_filters_bad_rooms_and_draws_player_last(self):
        runtime = self.ready_runtime()
        runtime.f.nearby = runtime.lua.table_from({
            '10': 0, '11': '1', '12': 2, '13': 3, '14': 4,
            '15': 1, '16': 2, '17': 1, '18': 1, '19': float('inf'),
            '20': -1, '21': 5, '22': float('nan'), '23': 1, '24': 1,
            '25': 1, '26': 1.5, 'bad': 1, '-1': 1,
        })
        for number, values in {
            11: dict(x='1', y='0', z='0'),
            12: dict(x=0, y=1, z=0),
            13: dict(x=-1, y=0, z=0),
            14: dict(x=0, y=-1, z=0),
            15: dict(x=1, y=1, z=1),  # A different floor.
            16: dict(x=99, y=0, z=0),  # A valid but off-canvas room.
            17: dict(x=float('nan'), y=0, z=0),
            18: dict(x=0, y=float('inf'), z=0),
            19: dict(x=1, y=1, z=0),
            20: dict(x=1, y=1, z=0),
            21: dict(x=1, y=1, z=0),
            22: dict(x=1, y=1, z=0),
            23: dict(x=1, z=0),
            24: dict(x=' ', y=0, z=0),
            26: dict(x=1, y=1, z=0),
        }.items():
            runtime.f.rooms[number] = runtime.table(**values)
        runtime.f.rooms[25] = 'malformed room'
        runtime.f.drawings = runtime.lua.table()
        runtime.f.mapUpdateCallback()
        self.assertEqual((runtime.f.nearbyRoom, runtime.f.nearbyRange), (10, 4))
        dots = [item for item in self.drawings(runtime, 'circle') if item.r == 3]
        self.assertEqual({(item.x, item.y, item.fill) for item in dots}, {
            (132, 110, '#7CFFB2'), (110, 132, '#4FD1C5'),
            (88, 110, '#3B82C4'), (110, 88, '#5A5F8A'),
        })
        player = self.drawings(runtime)[-1]
        self.assertEqual((player.kind, player.r, player.x, player.y, player.fill),
                         ('circle', 4, 110, 110, '#FFD166'))
        self.assertEqual(runtime.f.mapWrites, 0)

    def test_stationary_map_updates_and_resize_read_current_dimensions_and_font(self):
        runtime = self.ready_runtime()
        radar_id, _ = self.widget(runtime, 'radar')
        count = len(self.drawings(runtime))
        runtime.f.mapUpdateCallback()
        self.assertGreater(len(self.drawings(runtime)), count)
        runtime.f.drawings = runtime.lua.table()
        runtime.f.active = 'another-widget'
        runtime.f.canvasWidth = 320
        runtime.f.canvasHeight = 180
        runtime.f.widgetFont = '24px Changed'
        runtime.f.widgetEvents[radar_id].resize(runtime.table(width=999, height=999))
        player = self.drawings(runtime)[-1]
        self.assertEqual((player.x, player.y), (160, 90))
        self.assertTrue(all(item.active == radar_id for item in self.drawings(runtime)))
        for item in self.drawings(runtime, 'text'):
            self.assertIsNone(item.fontOverride)
            self.assertEqual(item.font, '24px Changed')

    def test_toggle_uses_live_visibility_and_only_command_forces_show_hide(self):
        runtime = self.ready_runtime()
        radar_id, radar = self.widget(runtime, 'radar')
        self.assertEqual(list(runtime.f.visibilityWrites), [])
        radar.visible = False  # Saved layout or a native close button.
        toggle = self.alias(runtime)
        before = len(self.drawings(runtime))
        toggle(runtime.lua.table_from(['toolbox-radar']))
        self.assertTrue(radar.visible)
        self.assertGreater(len(self.drawings(runtime)), before)
        toggle(runtime.lua.table_from(['toolbox-radar']))
        self.assertFalse(radar.visible)
        self.assertEqual([(item.key, item.visible, item.force)
                          for _, item in runtime.f.visibilityWrites.items()],
                         [(radar_id, True, True), (radar_id, False, True)])

    def test_disconnected_clicks_and_timer_refusal_do_not_strand_highlights(self):
        runtime = self.ready_runtime()
        click = runtime.f.roomClickCallback
        click(10)
        self.assertTrue(any('Origin' in value for _, value in runtime.f.outputs.items()))
        self.assertEqual(list(runtime.f.highlights), [])
        self.assertEqual(list(runtime.f.timers), [])
        runtime.f.connected = True
        runtime.f.noSession = True
        click(10)
        self.assertEqual(list(runtime.f.highlights), [])
        self.assertEqual(list(runtime.f.timers), [])
        runtime.f.noSession = False
        runtime.f.highlightRefused = True
        click(10)
        self.assertEqual(list(runtime.f.highlights), [])
        self.assertEqual(list(runtime.f.timers), [])
        runtime.f.highlightRefused = False
        click(10)
        self.assertEqual(list(runtime.f.highlights), [10])
        runtime.f.timerRefused = True
        click(10)
        self.assertEqual(list(runtime.f.highlights), [])
        self.assertEqual(list(runtime.f.timers), [])
        before = len(list(runtime.f.outputs))
        for value in (None, 'bad', float('nan'), float('inf'), -1):
            click(value)
        self.assertEqual(len(list(runtime.f.outputs)), before)
        self.assertEqual(list(runtime.f.highlights), [])

    def test_latest_click_replaces_flash_and_timer_with_session_specific_cleanup(self):
        runtime = self.ready_runtime()
        runtime.f.connected = True
        runtime.f.rooms[11] = runtime.table(name='Next', x=1, y=0, z=0)
        click = runtime.f.roomClickCallback
        click('10')
        first_key, first_timer = runtime.only(runtime.f.timers)
        self.assertEqual((first_timer.ms, first_timer.repeating), (3000, False))
        self.assertEqual(list(runtime.f.highlights), [10])
        click(11)
        second_key, second_timer = runtime.only(runtime.f.timers)
        self.assertNotEqual(first_key, second_key)
        self.assertEqual(list(runtime.f.highlights), [11])
        first_timer.callback()  # Canceled callbacks must not clear a newer flash.
        self.assertEqual(list(runtime.f.highlights), [11])
        runtime.g.onDisconnect('other-session')
        self.assertEqual(list(runtime.f.highlights), [11])
        self.assertEqual(list(runtime.f.timers), [second_key])
        runtime.g.onDisconnect('alpha')
        self.assertEqual(list(runtime.f.highlights), [])
        self.assertEqual(list(runtime.f.timers), [])
        click(10)
        expired_key, expired = runtime.only(runtime.f.timers)
        runtime.f.timers[expired_key] = None  # Host consumes a one-shot before callback.
        expired.callback()
        self.assertEqual(list(runtime.f.highlights), [])
        self.assertEqual(list(runtime.f.timers), [])
        click(11)
        _, cleanup_timer = runtime.only(runtime.f.timers)
        runtime.g.cleanup()
        cleanup_timer.callback()
        self.assertEqual(list(runtime.f.highlights), [])
        self.assertEqual(list(runtime.f.timers), [])

    def test_cleanup_destroys_widgets_and_all_late_callbacks_are_inert(self):
        runtime = self.ready_runtime()
        radar_id, _ = self.widget(runtime, 'radar')
        callbacks = [runtime.f.mapReadyCallback, runtime.f.roomChangeCallback,
                     runtime.f.mapUpdateCallback, runtime.f.widgetEvents[radar_id].resize]
        click, toggle = runtime.f.roomClickCallback, self.alias(runtime)
        runtime.g.cleanup()
        runtime.g.cleanup()
        before = (len(self.drawings(runtime)), len(list(runtime.f.outputs)))
        for callback in callbacks:
            callback()
        click(10)
        toggle(runtime.lua.table_from(['toolbox-radar']))
        self.assertEqual(list(runtime.f.widgets), [])
        self.assertEqual(len(list(runtime.f.destroyed)), 2)
        self.assertEqual(list(runtime.f.timers), [])
        self.assertEqual((len(self.drawings(runtime)), len(list(runtime.f.outputs))), before)
        cold = Runtime('mapper-minimap.lua')
        cold.g.init()
        cold.g.cleanup()
        cold.f.ready = True
        cold.f.mapReadyCallback()
        self.assertEqual(list(cold.f.widgets), [])


if __name__ == '__main__':
    unittest.main()
