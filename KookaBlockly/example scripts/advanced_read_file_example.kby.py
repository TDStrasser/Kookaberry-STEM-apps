import machine, kooka
import fonts

filename = None
f = None
line = None



# On-start code, run once at start-up.
if True:
    # Open the text file for reading
    filename = 'my_file.txt'
    kooka.display.setfont(fonts.mono6x7)
    kooka.display.print('Printing', filename, show=0)
    f = open(filename,"rt")
    # Loop that reads and prints each line of the file
    for line in f:
        kooka.display.print(line, show=0)
    kooka.display.print('End', show=0)

# Main loop code, run continuously.
while True:
    kooka.display.show()
    machine.idle()

# Generated Blockly XML follows
# <xml xmlns="https://developers.google.com/blockly/xml"><variables><variable id="f6N3ta#C#-hK,z+,_eU9">filename</variable><variable id="u/}7Qk]8[%|(s-MJw@u%">f</variable><variable id="d-2;ElO$QEN8NK~a-Me@">line</variable></variables><block type="event_on_start" id="L%w]A!4LN9IUJa$iVDt0" x="130" y="-30"><statement name="DO"><block type="py_stmt" id="_?#k,-#BR~}msmF2wpir"><field name="STMT"># Open the text file for reading</field><next><block type="variables_set" id="~1DgeZX}e^jK1$AQ0{@D"><field name="VAR" id="f6N3ta#C#-hK,z+,_eU9">filename</field><value name="VALUE"><block type="text" id="H2,zy}Oy6aKT%wgg=lX7"><field name="TEXT">my_file.txt</field></block></value><next><block type="display_setfont" id="eX$x%M4DohUPsEOO*pw{"><field name="FONT">mono6x7</field><next><block type="display_print2" id="iUbQpEq-Tq*dF.hbFO]7"><value name="VALUE1"><shadow type="text" id="KAyI[7E_pz/+);r}iosH"><field name="TEXT">Printing</field></shadow></value><value name="VALUE2"><shadow type="math_number" id="rTwsv4-`c%g)*,r@9=^8"><field name="NUM">123</field></shadow><block type="variables_get" id="(eF#is0t4(me/u|OtuP|"><field name="VAR" id="f6N3ta#C#-hK,z+,_eU9">filename</field></block></value><next><block type="variables_set" id="l7a0IN]^KxbEmX@TG)9z"><field name="VAR" id="u/}7Qk]8[%|(s-MJw@u%">f</field><value name="VALUE"><block type="py_expr" id="91L+wM.PFsv]P{6_^3PY"><field name="EXPR">open(filename,"rt")</field></block></value><next><block type="py_stmt" id="}id_bTg;lzB?NBJ2?8[u"><field name="STMT"># Loop that reads and prints each line of the file</field><next><block type="controls_forEach" id="MV,b{,sxw^I%9gh^4zx-"><field name="VAR" id="d-2;ElO$QEN8NK~a-Me@">line</field><value name="LIST"><block type="variables_get" id="tfW0Hj7/8?03t6xWX?97"><field name="VAR" id="u/}7Qk]8[%|(s-MJw@u%">f</field></block></value><statement name="DO"><block type="display_print" id="3|gTIn)aoP7h]?A$Xk$N"><value name="VALUE"><shadow type="text" id=";~`Adf4:E+N+]Bd+CKX_"><field name="TEXT">Hello</field></shadow><block type="variables_get" id="n8ln3WejpB$Lh:mC~`td"><field name="VAR" id="d-2;ElO$QEN8NK~a-Me@">line</field></block></value></block></statement><next><block type="display_print" id="!K#wL_h*Q1-_65s`]{Re"><value name="VALUE"><shadow type="text" id="iY70@9Kyexd4oiR.w@ER"><field name="TEXT">End</field></shadow></value></block></next></block></next></block></next></block></next></block></next></block></next></block></next></block></statement></block></xml>
