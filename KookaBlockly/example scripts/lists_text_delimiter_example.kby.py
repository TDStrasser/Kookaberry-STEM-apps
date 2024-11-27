import machine, kooka

list2 = None


list2 = 'alpha,beta,gamma,delta'.split(',')
kooka.display.print(','.join(list2), show=0)

kooka.display.show()

# Generated Blockly XML follows
# <xml xmlns="https://developers.google.com/blockly/xml"><variables><variable id="b0D2eNTL,zd$_BU[hn)p">list</variable></variables><block type="variables_set" id="[hq(#$%Jl31|qC`MTW_-" x="-210" y="-10"><field name="VAR" id="b0D2eNTL,zd$_BU[hn)p">list</field><value name="VALUE"><block type="lists_split" id="^tA1PJy(g8/S6kD@K@E~"><mutation mode="SPLIT"></mutation><field name="MODE">SPLIT</field><value name="INPUT"><block type="text" id="GbHkjX;9DH;eH5CgV$[c"><field name="TEXT">alpha,beta,gamma,delta</field></block></value><value name="DELIM"><shadow type="text" id="VU.tvz7`fnTks/e~3r:0"><field name="TEXT">,</field></shadow></value></block></value><next><block type="display_print" id="i(l_kIrDY]=hE^+/MsI_"><value name="VALUE"><shadow type="text" id="@4)Z|QN(PFedG)R-%5}X"><field name="TEXT">Hello</field></shadow><block type="lists_split" id="XB0Z),#l~Vd#M+D@[,Pl"><mutation mode="JOIN"></mutation><field name="MODE">JOIN</field><value name="INPUT"><block type="variables_get" id="CFAk#Y!.5[=C~E-#+eIF"><field name="VAR" id="b0D2eNTL,zd$_BU[hn)p">list</field></block></value><value name="DELIM"><shadow type="text" id="K66,jmkipi:E.]P+{0Xx"><field name="TEXT">,</field></shadow></value></block></value></block></next></block></xml>
