import machine, kooka

list2 = None


list2 = ['alpha', 'beta', 'gamma']
list2.append('delta')

# Generated Blockly XML follows
# <xml xmlns="https://developers.google.com/blockly/xml"><variables><variable id="b0D2eNTL,zd$_BU[hn)p">list</variable></variables><block type="variables_set" id="[hq(#$%Jl31|qC`MTW_-" x="-210" y="-10"><field name="VAR" id="b0D2eNTL,zd$_BU[hn)p">list</field><value name="VALUE"><block type="lists_create_with" id="*}W@dSs2iH72[}-v0^(d"><mutation items="3"></mutation><value name="ADD0"><block type="text" id="GbHkjX;9DH;eH5CgV$[c"><field name="TEXT">alpha</field></block></value><value name="ADD1"><block type="text" id=",|_bIN*3^`To$5ASJjxl"><field name="TEXT">beta</field></block></value><value name="ADD2"><block type="text" id="}.-Cpf}!vt@?l2=kH@(}"><field name="TEXT">gamma</field></block></value></block></value><next><block type="lists_setIndex" id=")D56RaLF1/c?SWC#UtzX"><mutation at="false"></mutation><field name="MODE">INSERT</field><field name="WHERE">LAST</field><value name="LIST"><block type="variables_get" id="/a66OeUy;b.f@eg?}w}v"><field name="VAR" id="b0D2eNTL,zd$_BU[hn)p">list</field></block></value><value name="TO"><block type="text" id="Hf}px}=LZ8Ie)RB}k|lR"><field name="TEXT">delta</field></block></value></block></next></block></xml>
