# Limits the number of cycles an IMA runs in case it doesn't halt
cycles_max = 1800
infinity = 1000

############################################
## Technology constants for all the modules
############################################

# IMA
vdd = 0.9
xbar_out_min = -10e-10
xbar_out_max = 1 # think about this - ???

########################################
## Define commonly used data structures
########################################
# List of supported opcodes for tile
op_list_tile = ['send', 'receive', 'compute']

# Instruction format for Tile
dummy_instrn_tile = {'opcode' : op_list_tile[0],
                     'mem_addr': 0,     # send/receive - edram_addr
                     'r2': 0,     # send-target_addr, receive-null
                     'neuron_id': 0, # send/receive-neuron_id
                     'ima_nma': 0 }      # compute - a bit for each ima

# List of supported opcodes/aluops for IMA
op_list = ['ld', 'st', 'alu', 'alui', 'mvm', 'hlt']
aluop_list = ['add', 'sub', 'sna', 'mul', 'sigmoid'] # sna is also used by mvm isntruction

# Instruction format for IMA
dummy_instrn = {'opcode' : op_list[0],      # instrn op
               'aluop'  : aluop_list[0],   # alu function
               'd1'     : 0,               # destination
               'r1'     : 0,               # operand1
               'r2'     : 0,               # operand2
               'addr'   : 0,               # ext_mem (edram) address
               'imm'    : 0,               # immediate (scalar) data
               'xb_nma' : 0 }              # xbar negative-mask, a xbar evaluates if neg-mask = 1

# List of pipeline stages - in order for IMA
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
num_xbar = 6
xbar_size = 4
dac_res = 2
adc_res = 2
num_adc = 6
num_ALU = 1
dataMem_size = 16
instrnMem_size = 80
data_width = 8 # (microarchitecture param)
xbdata_width = 8 # (nn speciic for now)

# Enter IMA component latency
xbar_lat = 17
dac_lat = 1
adc_lat = 1
snh_lat = 1
mux_lat = 1
alu_lat = 1
mem_lat = 1
# Added here for simplicity now (***needs modification later***)
memInterface_lat = infinity # infinite latency

#################################################
# Tile Hierarchy
    # Number of IMAs
    # EDRAM size
    # Shared Bus width
#################################################

# Enter parameters here:
num_ima = 2
#edram_buswidth = 16
edram_buswidth = data_width
edram_size = 32
receivebuff_size = 4 # size of receive buffer

# Enter component latency
tile_instrnMem_size = 20
edram_lat = 4


