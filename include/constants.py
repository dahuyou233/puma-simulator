###################################################################
## Technology constants for all the modules (components in an IMA)
###################################################################

vdd = 0.9
xbar_out_min = -10e-10
xbar_out_max = 1 # think about this - ???
data_width = 8 # (microarchitecture param)
xbdata_width = 8 # (nn speciic for now)
###################################
## Define commonly used structures
###################################

# Limits teyh number of cycles an IMA runs in case it doesn't halt
cycles_max = 60

# List of supported opcodes/aluops
op_list = ['ld', 'st', 'alu', 'alui', 'mvm', 'hlt']
aluop_list = ['add', 'sub', 'sna'] # sna is also used by mvm isntruction

# Instruction format
dummy_instrn = {'opcode' : op_list[0],      # instrn op
               'aluop'  : aluop_list[0],   # alu function
               'd1'     : 0,               # destination
               'r1'     : 0,               # operand1
               'r2'     : 0,               # opearnd2
               'addr'   : 0,               # ext_mem (edram) address
               'imm'    : 0,               # immediate (scalar) data
               'xb_nma' : 0 }              # xbar negative-mask, a xbar evaluates if neg-mask = 1

# List of pipeline stages - in order
stage_list = ['fet', 'dec', 'ex']
last_stage = 'ex'
#################################################
# DPE Hardware Configuration Parameters
#################################################

#################################################
# IMA Hierarchy
    # Number of Xbars
    # Crossbar Size
    # Bit resolution of ADCs and DACs
    # Number of ADCs
    # Number of ALUs
    # Data memory, Xbar in/out memory (Register) & Instruction memory sizes
#################################################

# Enter parameters here:
num_xbar = 2
xbar_size = 2
dac_res = 2
adc_res = 2
num_adc = 2
num_ALU = 1
dataMem_size = 16
instrnMem_size = 20

# Enter IMA component latency
xbar_lat = 6
dac_lat = 1
adc_lat = 1
snh_lat = 1
mux_lat = 1
alu_lat = 1
mem_lat = 1
# Added here for simplicity now (***needs modification later***)
memInterface_lat = 1
