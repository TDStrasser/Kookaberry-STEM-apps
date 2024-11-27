import machine, kooka

list2 = None


list2 = ['alpha', 'beta', 'gamma']
kooka.display.print('Length of list is', len(list2), show=0)

kooka.display.show()

# Generated Blockly XML follows
# <xml xmlns="https://developers.google.com/blockly/xml"><variables><variable id="b0D2eNTL,zd$_BU[hn)p">list</variable></variables><block type="variables_set" id="[hq(#$%Jl31|qC`MTW_-" x="-210" y="-10"><field name="VAR" id="b0D2eNTL,zd$_BU[hn)p">list</field><value name="VALUE"><block type="lists_create_with" id="*}W@dSs2iH72[}-v0^(d"><mutation items="3"></mutation><value name="ADD0"><block type="text" id="GbHkjX;9DH;eH5CgV$[c"><field name="TEXT">alpha</field></block></value><value name="ADD1"><block type="text" id=",|_bIN*3^`To$5ASJjxl"><field name="TEXT">beta</field></block></value><value name="ADD2"><block type="text" id="}.-Cpf}!vt@?l2=kH@(}"><field name="TEXT">gamma</field></block></value></block></value><next><block type="display_print2" id="V$CNj0r=nqUN@P2ux:|3"><value name="VALUE1"><shadow type="text" id="#geE|+luCFa$@6x6@|ck"><field name="TEXT">Length of list is</field></shadow></value><value name="VALUE2"><shadow type="math_number" id="~mT:w]85$KJ!c,?U30DH"><field name="NUM">123</field></shadow><block type="lists_length" id=".3qt0(Q_$+~~(Zz$ARHZ"><value name="VALUE"><block type="variables_get" id="{,@yjXW^*cInSx3l(^Pb"><field name="VAR" id="b0D2eNTL,zd$_BU[hn)p">list</field></block></value></block></value></block></next></block></xml>
