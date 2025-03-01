import pytest

from .. import *
# this is not necessary but mypy complains if it's not included
from .. import CompileOptions

options = CompileOptions()

def test_on_complete():
    assert OnComplete.NoOp.__teal__(options)[0] == TealSimpleBlock([
        TealOp(OnComplete.NoOp, Op.int, "NoOp")
    ])

    assert OnComplete.OptIn.__teal__(options)[0] == TealSimpleBlock([
        TealOp(OnComplete.OptIn, Op.int, "OptIn")
    ])

    assert OnComplete.CloseOut.__teal__(options)[0] == TealSimpleBlock([
        TealOp(OnComplete.CloseOut, Op.int, "CloseOut")
    ])

    assert OnComplete.ClearState.__teal__(options)[0] == TealSimpleBlock([
        TealOp(OnComplete.ClearState, Op.int, "ClearState")
    ])

    assert OnComplete.UpdateApplication.__teal__(options)[0] == TealSimpleBlock([
        TealOp(OnComplete.UpdateApplication, Op.int, "UpdateApplication")
    ])

    assert OnComplete.DeleteApplication.__teal__(options)[0] == TealSimpleBlock([
        TealOp(OnComplete.DeleteApplication, Op.int, "DeleteApplication")
    ])

def test_app_id():
    expr = App.id()
    assert expr.type_of() == TealType.uint64
    with TealComponent.Context.ignoreExprEquality():
        assert expr.__teal__(options)[0] == Global.current_application_id().__teal__(options)[0]

def test_opted_in():
    args = [Int(1), Int(12)]
    expr = App.optedIn(args[0], args[1])
    assert expr.type_of() == TealType.uint64
    
    expected = TealSimpleBlock([
        TealOp(args[0], Op.int, 1),
        TealOp(args[1], Op.int, 12),
        TealOp(expr, Op.app_opted_in)
    ])
    
    actual, _ = expr.__teal__(options)
    actual.addIncoming()
    actual = TealBlock.NormalizeBlocks(actual)
    
    assert actual == expected

def test_local_get():
    args = [Int(0), Bytes("key")]
    expr = App.localGet(args[0], args[1])
    assert expr.type_of() == TealType.anytype
    
    expected = TealSimpleBlock([
        TealOp(args[0], Op.int, 0),
        TealOp(args[1], Op.byte, "\"key\""),
        TealOp(expr, Op.app_local_get)
    ])
    
    actual, _ = expr.__teal__(options)
    actual.addIncoming()
    actual = TealBlock.NormalizeBlocks(actual)
    
    assert actual == expected

def test_local_get_invalid():
    with pytest.raises(TealTypeError):
        App.localGet(Txn.sender(), Bytes("key"))
    
    with pytest.raises(TealTypeError):
        App.localGet(Int(0), Int(1))

def test_local_get_ex():
    args = [Int(0), Int(6), Bytes("key")]
    expr = App.localGetEx(args[0], args[1], args[2])
    assert expr.type_of() == TealType.none
    assert expr.value().type_of() == TealType.anytype
    
    expected = TealSimpleBlock([
        TealOp(args[0], Op.int, 0),
        TealOp(args[1], Op.int, 6),
        TealOp(args[2], Op.byte, "\"key\""),
        TealOp(expr, Op.app_local_get_ex),
        TealOp(None, Op.store, expr.slotOk),
        TealOp(None, Op.store, expr.slotValue)
    ])
    
    actual, _ = expr.__teal__(options)
    actual.addIncoming()
    actual = TealBlock.NormalizeBlocks(actual)
    
    with TealComponent.Context.ignoreExprEquality():
        assert actual == expected

def test_local_get_ex_invalid():
    with pytest.raises(TealTypeError):
        App.localGetEx(Txn.sender(), Int(0), Bytes("key"))
    
    with pytest.raises(TealTypeError):
        App.localGetEx(Int(0), Bytes("app"), Bytes("key"))

    with pytest.raises(TealTypeError):
        App.localGetEx(Int(0), Int(0), Int(1))

def test_global_get():
    arg = Bytes("key")
    expr = App.globalGet(arg)
    assert expr.type_of() == TealType.anytype
    
    expected = TealSimpleBlock([
        TealOp(arg, Op.byte, "\"key\""),
        TealOp(expr, Op.app_global_get)
    ])
    
    actual, _ = expr.__teal__(options)
    actual.addIncoming()
    actual = TealBlock.NormalizeBlocks(actual)
    
    assert actual == expected

def test_global_get_invalid():
    with pytest.raises(TealTypeError):
        App.globalGet(Int(7))

def test_global_get_ex():
    args = [Int(6), Bytes("key")]
    expr = App.globalGetEx(args[0], args[1])
    assert expr.type_of() == TealType.none
    assert expr.value().type_of() == TealType.anytype
    
    expected = TealSimpleBlock([
        TealOp(args[0], Op.int, 6),
        TealOp(args[1], Op.byte, "\"key\""),
        TealOp(expr, Op.app_global_get_ex),
        TealOp(None, Op.store, expr.slotOk),
        TealOp(None, Op.store, expr.slotValue)
    ])
    
    actual, _ = expr.__teal__(options)
    actual.addIncoming()
    actual = TealBlock.NormalizeBlocks(actual)
    
    with TealComponent.Context.ignoreExprEquality():
        assert actual == expected

def test_global_get_ex_invalid():
    with pytest.raises(TealTypeError):
        App.globalGetEx(Bytes("app"), Bytes("key"))

    with pytest.raises(TealTypeError):
        App.globalGetEx(Int(0), Int(1))

def test_local_put():
    args = [Int(0), Bytes("key"), Int(5)]
    expr = App.localPut(args[0], args[1], args[2])
    assert expr.type_of() == TealType.none
    
    expected = TealSimpleBlock([
        TealOp(args[0], Op.int, 0),
        TealOp(args[1], Op.byte, "\"key\""),
        TealOp(args[2], Op.int, 5),
        TealOp(expr, Op.app_local_put)
    ])
    
    actual, _ = expr.__teal__(options)
    actual.addIncoming()
    actual = TealBlock.NormalizeBlocks(actual)
    
    assert actual == expected

def test_local_put_invalid():
    with pytest.raises(TealTypeError):
        App.localPut(Txn.sender(), Bytes("key"), Int(5))
    
    with pytest.raises(TealTypeError):
        App.localPut(Int(1), Int(0), Int(5))
    
    with pytest.raises(TealTypeError):
        App.localPut(Int(1), Bytes("key"), Pop(Int(1)))

def test_global_put():
    args = [Bytes("key"), Int(5)]
    expr = App.globalPut(args[0], args[1])
    assert expr.type_of() == TealType.none
    
    expected = TealSimpleBlock([
        TealOp(args[0], Op.byte, "\"key\""),
        TealOp(args[1], Op.int, 5),
        TealOp(expr, Op.app_global_put)
    ])
    
    actual, _ = expr.__teal__(options)
    actual.addIncoming()
    actual = TealBlock.NormalizeBlocks(actual)
    
    assert actual == expected

def test_global_put_invalid():
    with pytest.raises(TealTypeError):
        App.globalPut(Int(0), Int(5))
    
    with pytest.raises(TealTypeError):
        App.globalPut(Bytes("key"), Pop(Int(1)))

def test_local_del():
    args = [Int(0), Bytes("key")]
    expr = App.localDel(args[0], args[1])
    assert expr.type_of() == TealType.none
    
    expected = TealSimpleBlock([
        TealOp(args[0], Op.int, 0),
        TealOp(args[1], Op.byte, "\"key\""),
        TealOp(expr, Op.app_local_del)
    ])
    
    actual, _ = expr.__teal__(options)
    actual.addIncoming()
    actual = TealBlock.NormalizeBlocks(actual)
    
    assert actual == expected

def test_local_del_invalid():
    with pytest.raises(TealTypeError):
        App.localDel(Txn.sender(), Bytes("key"))
    
    with pytest.raises(TealTypeError):
        App.localDel(Int(1), Int(2))

def test_global_del():
    arg = Bytes("key")
    expr = App.globalDel(arg)
    assert expr.type_of() == TealType.none
    
    expected = TealSimpleBlock([
        TealOp(arg, Op.byte, "\"key\""),
        TealOp(expr, Op.app_global_del)
    ])
    
    actual, _ = expr.__teal__(options)
    actual.addIncoming()
    actual = TealBlock.NormalizeBlocks(actual)
    
    assert actual == expected

def test_global_del_invalid():
    with pytest.raises(TealTypeError):
        App.globalDel(Int(2))
