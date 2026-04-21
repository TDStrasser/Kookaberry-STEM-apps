import machine, kooka

list2 = None
sublist = None


list2 = ['alpha', 'beta', 'gamma', 'delta']
sublist = list2[123 : ]

# Generated Blockly XML follows
# <xml xmlns="https://developers.google.com/blockly/xml"><variables><variable id="b0D2eNTL,zd$_BU[hn)p">list</variable><variable id="E!;d}/7RyY/fs^}l6wjV">sublist</variable></variables><block type="variables_set" id="[hq(#$%Jl31|qC`MTW_-" x="-210" y="-10"><field name="VAR" id="b0D2eNTL,zd$_BU[hn)p">list</field><value name="VALUE"><block type="lists_create_with" id="*}W@dSs2iH72[}-v0^(d"><mutation items="4"></mutation><value name="ADD0"><block type="text" id="GbHkjX;9DH;eH5CgV$[c"><field name="TEXT">alpha</field></block></value><value name="ADD1"><block type="text" id=",|_bIN*3^`To$5ASJjxl"><field name="TEXT">beta</field></block></value><value name="ADD2"><block type="text" id="}.-Cpf}!vt@?l2=kH@(}"><field name="TEXT">gamma</field></block></value><value name="ADD3"><block type="text" id="Hf}px}=LZ8Ie)RB}k|lR"><field name="TEXT">delta</field></block></value></block></value><next><block type="variables_set" id="JHvXnZ,$duosY8QTdxQ~"><field name="VAR" id="E!;d}/7RyY/fs^}l6wjV">sublist</field><value name="VALUE"><block type="lists_getSublist" id="_cj=Qd@R%_+bxTqQQ7M6"><mutation at1="true" at2="false"></mutation><field name="WHERE1">FROM_START</field><field name="WHERE2">LAST</field><value name="LIST"><block type="variables_get" id="??*pcZpE;7dxD}ot!-2u"><field name="VAR" id="b0D2eNTL,zd$_BU[hn)p">list</field></block></value><value name="AT1"><block type="math_number" id="hxZS?99STISE1Caq}t~;"><field name="NUM">123</field></block></value></block></value></block></next></block></xml>
