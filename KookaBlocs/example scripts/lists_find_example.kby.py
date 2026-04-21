import machine, kooka

list2 = None

def first_index(my_list, elem):
    try: index = my_list.index(elem)
    except: index = -1
    return index


list2 = ['alpha', 'beta', 'gamma']
kooka.display.print('Index is', first_index(list2, 'gamma'), show=0)

kooka.display.show()

# Generated Blockly XML follows
# <xml xmlns="https://developers.google.com/blockly/xml"><variables><variable id="b0D2eNTL,zd$_BU[hn)p">list</variable></variables><block type="variables_set" id="[hq(#$%Jl31|qC`MTW_-" x="-210" y="-10"><field name="VAR" id="b0D2eNTL,zd$_BU[hn)p">list</field><value name="VALUE"><block type="lists_create_with" id="*}W@dSs2iH72[}-v0^(d"><mutation items="3"></mutation><value name="ADD0"><block type="text" id="GbHkjX;9DH;eH5CgV$[c"><field name="TEXT">alpha</field></block></value><value name="ADD1"><block type="text" id=",|_bIN*3^`To$5ASJjxl"><field name="TEXT">beta</field></block></value><value name="ADD2"><block type="text" id="}.-Cpf}!vt@?l2=kH@(}"><field name="TEXT">gamma</field></block></value></block></value><next><block type="display_print2" id="V$CNj0r=nqUN@P2ux:|3"><value name="VALUE1"><shadow type="text" id="#geE|+luCFa$@6x6@|ck"><field name="TEXT">Index is</field></shadow></value><value name="VALUE2"><shadow type="math_number" id="~mT:w]85$KJ!c,?U30DH"><field name="NUM">123</field></shadow><block type="lists_indexOf" id="1Bk0/JA,8MNkOJ((w];#"><field name="END">FIRST</field><value name="VALUE"><block type="variables_get" id="t9Py+a*QVG?uc5]K]FVy"><field name="VAR" id="b0D2eNTL,zd$_BU[hn)p">list</field></block></value><value name="FIND"><block type="text" id="p3MRbgt*{0XOcKtWX!o~"><field name="TEXT">gamma</field></block></value></block></value></block></next></block></xml>
