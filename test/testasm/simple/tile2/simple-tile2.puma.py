
import sys, os
import numpy as np
import math
sys.path.insert (0, '/home/fernandofelix/Workspace/dpe/training/dpe_emulate/include/')
sys.path.insert (0, '/home/fernandofelix/Workspace/dpe/training/dpe_emulate/src/')
from data_convert import *
from instrn_proto import *
from tile_instrn_proto import *
dict_temp = {}
dict_list = []
i_temp = i_receive(mem_addr=0, vtile_id=0, receive_width=5, counter=1, vec=1)
dict_list.append(i_temp.copy())
i_temp = i_send(mem_addr=5, vtile_id=2, send_width=5, target_addr=1, vec=1)
dict_list.append(i_temp.copy())
i_temp = i_halt()
dict_list.append(i_temp.copy())
filename = 'simple/tile2/tile_imem.npy'
np.save(filename, dict_list)