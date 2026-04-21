import machine, kooka

list2 = None


list2 = ['alpha', 'beta', 'gamma']
while not not len(list2):
    kooka.display.print('Item is', list2.pop(0), show=0)

kooka.display.show()

# Generated Blockly XML follows
# <xml xmlns="https://developers.google.com/blockly/xml"><variables><variable id="b0D2eNTL,zd$_BU[hn)p">list</variable></variables><block type="variables_set" id="[hq(#$%Jl31|qC`MTW_-" x="-210" y="-10"><field name="VAR" id="b0D2eNTL,zd$_BU[hn)p">list</field><value name="VALUE"><block type="lists_create_with" id="*}W@dSs2iH72[}-v0^(d"><mutation items="3"></mutation><value name="ADD0"><block type="text" id="GbHkjX;9DH;eH5CgV$[c"><field name="TEXT">alpha</field></block></value><value name="ADD1"><block type="text" id=",|_bIN*3^`To$5ASJjxl"><field name="TEXT">beta</field></block></value><value name="ADD2"><block type="text" id="}.-Cpf}!vt@?l2=kH@(}"><field name="TEXT">gamma</field></block></value></block></value><next><block type="controls_whileUntil" id="y*c,lyItV]kLLBezIUF]"><field name="MODE">UNTIL</field><value name="BOOL"><block type="lists_isEmpty" id="o8w}u`H8)KT[x:C3_cZ)"><value name="VALUE"><block type="variables_get" id="e!QF9F{N@5K9-`pfa7Pb"><field name="VAR" id="b0D2eNTL,zd$_BU[hn)p">list</field></block></value></block></value><statement name="DO"><block type="display_print2" id="V$CNj0r=nqUN@P2ux:|3"><value name="VALUE1"><shadow type="text" id="#geE|+luCFa$@6x6@|ck"><field name="TEXT">Item is</field></shadow></value><value name="VALUE2"><shadow type="math_number" id="~mT:w]85$KJ!c,?U30DH"><field name="NUM">123</field></shadow><block type="lists_getIndex" id="^0G~k~!e=msr%^sFKw4e"><mutation statement="false" at="false"></mutation><field name="MODE">GET_REMOVE</field><field name="WHERE">FIRST</field><value name="VALUE"><block type="variables_get" id="pN[2._qg2w{f^@*2P$x~"><field name="VAR" id="b0D2eNTL,zd$_BU[hn)p">list</field></block></value></block></value></block></statement></block></next></block></xml>
