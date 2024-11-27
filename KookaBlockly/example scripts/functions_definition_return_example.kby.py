import machine, kooka
import math

diameter = None

# Describe this function...
def circumference(diameter):
    return math.pi * diameter

# Generated Blockly XML follows
# <xml xmlns="https://developers.google.com/blockly/xml"><variables><variable id="_-7bH6]zzduhC}rISqYW">diameter</variable></variables><block type="procedures_defreturn" id="afY;-E8lFLia{~4m=1OL" x="130" y="10"><mutation><arg name="diameter" varid="_-7bH6]zzduhC}rISqYW"></arg></mutation><field name="NAME">circumference</field><comment pinned="false" h="80" w="160">Describe this function...</comment><value name="RETURN"><block type="math_arithmetic" id="d;t[s+fzv2_gqPa=eetx"><field name="OP">MULTIPLY</field><value name="A"><shadow type="math_number" id="I*O{Uq{8EkF_YsQmn,6?"><field name="NUM">1</field></shadow><block type="math_constant" id="3wu6|80_m;FdHr.wwz}g"><field name="CONSTANT">PI</field></block></value><value name="B"><shadow type="math_number" id="75}YH[;qmLMZGkz8FeU_"><field name="NUM">1</field></shadow><block type="variables_get" id="sY!PK1YoUw{aD,Le1V+%"><field name="VAR" id="_-7bH6]zzduhC}rISqYW">diameter</field></block></value></block></value></block></xml>
