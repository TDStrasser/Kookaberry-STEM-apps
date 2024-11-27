import machine, kooka
import fonts

i = None


kooka.display.setfont(fonts.mono6x7)
for i in range(1, 17, 3):
    kooka.display.print(i, show=0)
    kooka.display.show()

kooka.display.show()

# Generated Blockly XML follows
# <xml xmlns="https://developers.google.com/blockly/xml"><variables><variable id="lKox{@eWt-)#e~TdWm_G">i</variable></variables><block type="display_setfont" id="Fhg.#}l`kUl75jJ6H90+" x="270" y="-110"><field name="FONT">mono6x7</field><next><block type="controls_for" id="~%?LTSVD?[I`L:]`}.9~"><field name="VAR" id="lKox{@eWt-)#e~TdWm_G">i</field><value name="FROM"><block type="math_number" id="FmfN)Cu?K1/rx;QTB+(R"><field name="NUM">1</field></block></value><value name="TO"><block type="math_number" id="am*}oR(9a[mJet%X+w0d"><field name="NUM">16</field></block></value><value name="BY"><block type="math_number" id="`p:Hh-TSrGi`F$T7@an("><field name="NUM">3</field></block></value><statement name="DO"><block type="display_print" id="X?J`_VdB{V=PPJvt@JQG"><value name="VALUE"><shadow type="text" id="lIG}HE[_cYyND9(q0?zb"><field name="TEXT">Hello</field></shadow><block type="variables_get" id="{,WrFKtMNACUlXuRG*gq"><field name="VAR" id="lKox{@eWt-)#e~TdWm_G">i</field></block></value><next><block type="display_show" id="SB4_MUW];qgS}cH-zz?*"></block></next></block></statement></block></next></block></xml>
