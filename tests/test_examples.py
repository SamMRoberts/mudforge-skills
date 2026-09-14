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
  ready=false, rooms={}, mapWrites=0, drawings={}, active=nil
}
local function id(prefix)
  fixture.sequence = fixture.sequence + 1
  return prefix .. tostring(fixture.sequence)
end
function echo(value) table.insert(fixture.outputs, value) end
function getSessionId() return fixture.session end
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
  if not fixture.connected then return "" end
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
  fixture.widgetEvents[key]={}
  return key
end
function setWidgetProperty(key,prop,value)
  fixture.widgets[key][prop]=value
  if prop=="content" then fixture.contentWrites=fixture.contentWrites+1 end
end
function setBoundValues(key,values) fixture.bindings[key]=values end
function registerWidgetEvent(key,event,fn) fixture.widgetEvents[key][event]=fn end
function destroyWidget(key)
  fixture.widgets[key]=nil
  fixture.widgetEvents[key]=nil
  fixture.bindings[key]=nil
end
function setActiveWidget(key) fixture.active=key end
function clear(color) table.insert(fixture.drawings,{kind="clear",active=fixture.active,color=color}) end
function drawRect(x,y,w,h,color,stroke)
  assert(type(x)=="number" and fixture.active, "incorrect drawing signature")
  table.insert(fixture.drawings,{kind="rect",active=fixture.active,w=w,h=h})
end
function drawText(text,x,y,color,font)
  assert(type(x)=="number" and fixture.active, "incorrect drawing signature")
  table.insert(fixture.drawings,{kind="text",active=fixture.active,text=text})
end
function isMapReady() return fixture.ready end
function onMapReady(fn) fixture.mapReadyCallback=fn end
function getPlayerRoom() return fixture.currentRoom end
function getMapRoom(key) return fixture.rooms[key] end
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
        self.assertEqual(len(files), 9)
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
        self.assertIsNone(trigger.callback(runtime.lua.table_from(match.groups())))
        self.assertEqual(runtime.f.vars.score, '42')
        self.assertIsNone(re.fullmatch(trigger.pattern, 'Toolbox score: unavailable'))
        _, alias = runtime.only(runtime.f.aliases)
        self.assertEqual(alias.replacement, '')
        match = re.fullmatch(alias.pattern, 'toolbox-score 17')
        alias.callback(runtime.lua.table_from([match.group(0), *match.groups()]))
        self.assertEqual(runtime.f.vars.score, '17')

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
        runtime.f.widgetEvents[widget].action()
        self.assertEqual(runtime.f.bindings[widget].maximum, '?')
        runtime.command('toolbox-vitals-demo')
        runtime.g.onDisconnect('alpha')
        self.assertEqual(runtime.f.bindings[widget].hp, '?')
        runtime.g.cleanup()
        runtime.g.cleanup()
        self.assertEqual(list(runtime.f.widgets), [])
        # The runtime's textContent patch itself requires native verification.

    def test_canvas_selects_widget_and_reflows(self):
        runtime = Runtime('canvas-status.lua')
        runtime.g.init()
        widget, _ = runtime.only(runtime.f.widgets)
        self.assertEqual(runtime.f.drawings[2].w, 224)
        runtime.f.active = 'unrelated-widget'
        runtime.f.widgetEvents[widget].resize(runtime.table(width=320, height=120))
        self.assertEqual(runtime.f.drawings[5].active, widget)
        self.assertEqual(runtime.f.drawings[5].w, 304)
        self.assertEqual(runtime.f.drawings[5].h, 104)

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


if __name__ == '__main__':
    unittest.main()
