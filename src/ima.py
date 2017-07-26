# Defines a configurable IMA module with its methods

# add the folder location for include files
import sys, json
sys.path.insert (0, '/home/ankitaay/dpe/include')

# import dependancy files
import numpy as np
import constants as param
import ima_modules as imod

class ima (object):

    instances_created = 0

    #######################################################
    ### Instantiate different modules
    #######################################################
    def __init__ (self):

        # Assign a ima_id for identification purpose in debug trace
        self.ima_id = ima.instances_created
        ima.instances_created += 1

        ######################################################################
        ## Parametrically instantiate different physical IMA hardware modules
        ######################################################################
        # Instantiate crossbars
        self.xbar_list = []
        for i in xrange(param.num_xbar):
            temp_xbar = imod.xbar (param.xbar_size)
            self.xbar_list.append(temp_xbar)

        # Instantiate DACs
        self.dacArray_list = []
        for i in xrange(param.num_xbar):
            temp_dacArray = imod.dac_array (param.xbar_size, param.dac_res)
            self.dacArray_list.append(temp_dacArray)

        # Instatiate adcs
        self.adc_list = []
        for i in xrange(param.num_adc):
            temp_adc = imod.adc (param.adc_res)
            self.adc_list.append(temp_adc)

        # Instantiate sample and hold
        self.snh_list = []
        for i in xrange(param.num_xbar):
            temp_snh = imod.sampleNhold (param.xbar_size)
            self.snh_list.append(temp_snh)

        # Instatiate mux (num_mux depends on num_xbars and num_adcs)
        # The mux design (described below) will vary (xbar_size = 64):
        # For 2 xbars with 1 ADC : Two 64-1 mux and One 2-1 mux
        # For 2 xbars with 2 ADCs: Two 64-1 mux
        # Similarly, 8 xbars & 1 ADC: Eight 64-1 mux and One 8-1 mux
        # *** Number of "xbar_size" muxes = num_xbar ***
        # *** Number of "(num_xbar/num_adc)" muxes = num_adcs ***
        # A mux with inp_size = 1 is basically a dammy mux (wire)

        self.mux1_list = [] # from xbar
        inp1_size = param.xbar_size
        for i in xrange(param.num_xbar):
            temp_mux = imod.mux (inp1_size)
            self.mux1_list.append(temp_mux)

        self.mux2_list = [] # to adc
        inp2_size = param.num_xbar / param.num_adc
        for i in xrange(param.num_adc):
            temp_mux = imod.mux (inp2_size)
            self.mux2_list.append(temp_mux)

        # Instantiate ALUs
        self.alu_list = []
        for i in xrange(param.num_ALU):
            temp_alu = imod.alu ()
            self.alu_list.append(temp_alu)

        # Instantiate  data memory (stores data)
        self.dataMem = imod.memory (param.dataMem_size, param.num_xbar * param.xbar_size)

        # Instantiate multiple xbar input memories (stores xbar input data)
        self.xb_inMem_list = []
        for i in xrange (param.num_xbar):
            temp_xb_inMem = imod.xb_inMem (param.xbar_size)
            self.xb_inMem_list.append(temp_xb_inMem)

        # Instantiate multiple xbar output memories (stores xbar output data)
        self.xb_outMem_list = []
        for i in xrange (param.num_xbar):
            temp_xb_outMem = imod.xb_outMem (param.xbar_size)
            self.xb_outMem_list.append(temp_xb_outMem)

        # Instantiate instruction memory (stores instruction)
        self.instrnMem = imod.instrn_memory (param.instrnMem_size)

        # Instantiate the memory interface (interface to edram controller)
        self.mem_interface = imod.mem_interface ()

        #############################################################################################################
        ## Define virtual (currently for software emulation purpose (doesn't have a corresponding hardware currenty)
        #############################################################################################################

        # Define stage-wise pipeline registers (f - before fetch, fd -fetch_decode, de - decode_execute)
        self.pc = 0 # holds the next program counter value

        self.fd_instrn = param.dummy_instrn

        self.de_instrn = param.dummy_instrn # For Debug Only

        self.de_opcode = param.dummy_instrn['opcode']
        self.de_aluop = param.dummy_instrn['aluop']
        self.de_d1 = param.dummy_instrn['d1'] # target register addr for alu/alui/ld
        self.de_addr = param.dummy_instrn['addr'] # edram addr for ld/st
        self.de_imm = param.dummy_instrn['imm'] # imm value for alui
        self.de_xb_nma = param.dummy_instrn['xb_nma'] # nma value for xbar execution

        self.de_val1 = 0 # operand read from r1 address
        self.de_val2 = 0 # operand read from r2 address

        ########################################################
        ## Define book-keeping variables for pipeline execution
        ########################################################
        self.num_stage = len (param.stage_list)

        # Tells when EDRAM access for ld instruction is done
        self.ldAccess_done = 0

        # Define the book-keeping variables - stage-specific
        self.stage_empty = [0] * self.num_stage
        self.stage_cycle = [0] * self.num_stage
        self.stage_latency = [0] * self.num_stage # tells how many cycles will the current method running in a stage will require
        self.stage_done = [0] * self.num_stage

        # Define global pipeline variables
        self.debug = 0

        # Define a halt signal
        self.halt = 0


    ############################################################
    ### Define what a pipeline stage does for each instruction
    ############################################################
    # Increment stage cycles but update pipeline registers at end only when update_ready flag is set

    # "Fetch" stage (common to all instructions)
    def fetch (self, update_ready, fid):
        sId = 0 # sId - stageId

        # Define what to do in fetch
        def do_fetch (self):
            # commmon to all instructions
            self.fd_instrn = self.instrnMem.read (self.pc) # update pipeline register (fetch/decode)

            # A blan instruction signifies program end
            if (self.fd_instrn != ''):
                self.stage_empty[sId+1] = 0
                self.stage_done[sId+1] = 0

                self.pc = self.pc + 1 # update pipeline register before fetch stage
                # self.stage_empty[sId] = 1


        # Describe the functionality on a cycle basis
        # Start a fetch stage - if fetch stage is empty and succedding stage is done (update_ready)
        # Succeding stages back-propagate update_ready when they are done
        # For all other stages (except fetch) - start when stage is non-empty

        # State machine (lil different than other stages)
        # Describe the functionality on a cycle basis
        if (self.stage_empty[sId] != 1):
            # First cycle - update the target latency
            if (self.stage_cycle[sId] == 0):
                self.stage_latency[sId] = self.instrnMem.getLatency()

                # Check if first = last cycle
                if (self.stage_latency[sId] == 1 and update_ready):
                    do_fetch (self)
                    self.stage_done[sId] = 1
                    self.stage_cycle[sId] = 0
                    #self.stage_empty[sId] = 1
                else:
                    self.stage_cycle[sId] = self.stage_cycle[sId] + 1

            # Last cycle - update pipeline registers & done flag
            elif (self.stage_cycle[sId] >= self.stage_latency[sId]-1 and update_ready):
                do_fetch (self)
                self.stage_done[sId] = 1
                self.stage_cycle[sId] = 0
                #self.stage_empty[sId] = 1

            # For all other cycles
            else:
                self.stage_cycle[sId] = self.stage_cycle[sId] + 1


    # "Decode" stage - Reads operands (if needed) and puts into the specific data structures
    def decode (self, update_ready, fid):
        sId = 1

        # Define what to do in decode (done for conciseness)
        def do_decode (self, dec_op):
            # common to all instructions
            self.de_opcode = dec_op
            self.stage_empty[sId+1] = 0
            self.stage_done[sId+1] = 0

            self.de_instrn = self.fd_instrn # for DEBUG only

            # instruction specific (for eg: ld_dec - load's decode stage)
            if (dec_op == 'ld'):
                self.de_addr = self.fd_instrn['addr']
                self.de_d1 = self.fd_instrn['d1']

            elif (dec_op == 'st'):
                self.de_addr = self.fd_instrn['addr']

                # read the data from dataMem or xb_outMem depending on address
                st_data_addr =  self.fd_instrn['r1'] # address of data in register
                if (st_data_addr >= param.num_xbar * param.xbar_size):
                    self.de_val1 = self.dataMem.read (self.fd_instrn['r1'])
                else:
                    xb_id = st_data_addr / param.xbar_size
                    addr = st_data_addr % param.xbar_size
                    self.de_val1 = self.xb_outMem_list[xb_id].read (addr)

                # NEW - added store counter (comes from r2 and stored in val2)
                self.de_val2 = self.fd_instrn['r2']

            elif (dec_op == 'alu'):
                self.de_aluop = self.fd_instrn['aluop']
                self.de_d1 = self.fd_instrn['d1']
                val1_addr = self.fd_instrn['r1']
                val2_addr = self.fd_instrn['r2']

                # read val 1 either from data memory or xbar_outmem
                if (val1_addr >= param.num_xbar * param.xbar_size):
                    self.de_val1 = self.dataMem.read (self.fd_instrn['r1'])
                else:
                    xb_id = val1_addr / param.xbar_size
                    addr = val1_addr % param.xbar_size
                    self.de_val1 = self.xb_outMem_list[xb_id].read (addr)

                # read val 2 either from data memory or xbar_outmem
                if (val2_addr >= param.num_xbar * param.xbar_size):
                    self.de_val2 = self.dataMem.read (self.fd_instrn['r2'])
                else:
                    xb_id = val2_addr / param.num_xbar
                    addr = val2_addr % param.xbar_size
                    self.de_val2 = self.xb_outMem_list[xb_id].read (addr)

            elif (dec_op == 'alui'):
                self.de_aluop = self.fd_instrn['aluop']
                self.de_d1 = self.fd_instrn['d1']
                val1_addr = self.fd_instrn['r1']

                # read val 1 either from data memory or xbar_outmem
                if (val1_addr >= param.num_xbar * param.xbar_size):
                    self.de_val1 = self.dataMem.read (self.fd_instrn['r1'])
                else:
                    xb_id = val1_addr / param.num_xbar
                    addr = val1_addr % param.xbar_size
                    self.de_val1 = self.xb_outMem_list[xb_id].read (addr)

                self.de_val2 = self.fd_instrn['imm']

            elif (dec_op == 'mvm'):
                xb_nma = self.fd_instrn['xb_nma']
                assert (0 <= xb_nma <= param.num_xbar), 'unsupported xbar configuration'
                self.de_xb_nma = xb_nma


        # State machine runs only if the stage is non-empty
        # Describe the functionality on a cycle basis
        if (self.stage_empty[sId] != 1):
            # First cycle - update the target latency
            if (self.stage_cycle[sId] == 0):
                # Check for assertion pass
                dec_op = self.fd_instrn['opcode']
                assert (dec_op in param.op_list), 'unsupported opcode'

                self.stage_latency[sId] = self.dataMem.getLatency()

                # Check if first = last cycle
                if (self.stage_latency[sId] == 1 and update_ready):
                    do_decode (self, dec_op)
                    self.stage_done[sId] = 1
                    self.stage_cycle[sId] = 0
                    self.stage_empty[sId] = 1
                else:
                    self.stage_cycle[sId] = self.stage_cycle[sId] + 1

            # Last cycle - update pipeline registers (if ??) & done flag
            elif (self.stage_cycle[sId] >= self.stage_latency[sId]-1 and update_ready):
                dec_op = self.fd_instrn['opcode']
                do_decode (self, dec_op)
                self.stage_done[sId] = 1
                self.stage_cycle[sId] = 0
                self.stage_empty[sId] = 1

            # For all other cycles (non-first, non-last, non-update ready)
            else:
                self.stage_cycle[sId] = self.stage_cycle[sId] + 1


    # Execute stage - compute and store back to registers
    def execute (self, update_ready, fid):
        sId = 2

        # Define what to do in execute (done for conciseness)
        def do_execute (self, ex_op, fid):
            if (ex_op == 'ld'):
                self.ldAccess_done = 0
                data = self.mem_interface.ramload
                # based on the address write to dataMem or xb_inMem
                if (self.de_d1 >= param.num_xbar * param.xbar_size):
                    self.dataMem.write (self.de_d1, data)
                else:
                    xb_id = self.de_d1 / param.xbar_size
                    addr = self.de_d1 % param.xbar_size
                    self.xb_inMem_list[xb_id].write (addr, data)

            elif (ex_op == 'st'): #nothing to be done by ima for st here
                return 1

            elif (ex_op == 'alu'): #multiple ALUs in parallel will be used in ALUvec instrn
                # compute in ALU
                [out, ovf] = self.alu_list[0].propagate (self.de_val1, self.de_val2, self.de_aluop)
                if (ovf):
                    fid.write ('IMA: ' + str(self.ima_id) + ' ALU Overflow Exception ' +\
                            self.de_aluop + ' allowed to run')
                # write to dataMem - check if addr is a valid datamem address
                assert (self.de_d1 >= param.num_xbar * param.xbar_size), 'ALU instrn: datamemory write addrress is invalid'
                self.dataMem.write (self.de_d1, out)

            elif (ex_op == 'alui'):
                # compute in ALU
                [out, ovf] = self.alu_list[0].propagate (self.de_val1, self.de_val2, self.de_aluop)
                if (ovf):
                    fid.write ('IMA: ' + str(self.ima_id) + ' ALU Overflow Exception ' +\
                            self.de_aluop + ' allowed to run')
                # write to dataMem
                assert (self.de_d1 >= param.num_xbar * param.xbar_size), 'ALUi instrn: datamemory write addrress is invalid'
                self.dataMem.write (self.de_d1, out)

            elif (ex_op == 'mvm'):
                # traverse through the xbars - (nma is the number of crossbars which will evaluate)
                for i in xrange (self.de_xb_nma): # this 'for' across xbar outs to next mux can happen via mux
                    # reset the xb out memory before starting to accumulate
                    self.xb_outMem_list[i].reset ()

                    ## Loop to cover all bits of inputs
                    for k in xrange (param.xbdata_width / param.dac_res):
                        # read the values from the xbar's input register
                        out_xb_inMem = self.xb_inMem_list[i].read (param.dac_res)

                        #*************************************** HACK *********************************************
                        ###### CAUTION: Not replicated exact "functional" circuit behaviour for analog parts
                        ###### Use propagate (not propagate_hack) for DAC, Xbar, TIA, SNH, ADC when above is done
                        #*************************************** HACK *********************************************

                        # convert digital values to analog
                        out_dac = self.dacArray_list[i].propagate_dummy (out_xb_inMem) #pass through
                        # compute dot-product
                        out_xbar = self.xbar_list[i].propagate_dummy (out_dac)
                        # do sampling and hold
                        out_snh = self.snh_list[i].propagate_dummy (out_xbar)

                        for j in xrange (param.xbar_size): # this 'for' across xbar outs to adc happens via mux
                            # convert from analog to digital
                            adc_id = i % param.num_adc
                            out_mux1 = self.mux1_list[i].propagate_dummy (out_snh[j]) # i is the ith xbar
                            out_mux2 = self.mux2_list[i % param.num_adc].propagate_dummy (out_mux1)
                            out_adc = self.adc_list[adc_id].propagate_dummy (out_mux2)
                            # read from xbar's output register
                            out_xb_outMem = self.xb_outMem_list[i].read (j)
                            # shift and add - make a dedicated sna unit -- PENDING
                            alu_op = 'sna'
                            # modify (len(out_adc) to adc_res) when ADC functionality is implemented
                            out_adc = '0'*(param.xbdata_width - len(out_adc)) + out_adc
                            [out_sna, ovf] = self.alu_list[0].propagate (out_xb_outMem, out_adc, alu_op, k * param.dac_res)
                            if (param.debug and ovf):
                                fid.write ('IMA: ' + str(self.ima_id) + ' ALU Overflow Exception ' +\
                                        self.de_aluop + ' allowed to run')
                            # store back to xbar's output register & restart it
                            self.xb_outMem_list[i].write (out_sna)

                        self.xb_outMem_list[i].restart()

            else: # for halt instruction
                self.halt = 1


        # Computes the latency for mvm instruction based on DPE configuration
        def xbComputeLatency (self):
            # assumption1: num_adc = num_s&a = num_outReg_Ports
            # assumption2: an adc connects to only one xbar
            # assumption3: shift&add unit is seen as an alu for now
            # assumption4: two stage pipeline - unit1 & unit2 as shown below

            # using '\' to continue on enxt line
            latency_unit1 =  self.xb_inMem_list[0].getLatency() +\
                            self.dacArray_list[0].getLatency() +\
                            self.xbar_list[0].getLatency() +\
                            self.snh_list[0].getLatency()

            latency_unit2 = param.xbar_size * (self.mux1_list[0].getLatency() +\
                                               self.mux2_list[0].getLatency() +\
                                               self.adc_list[0].getLatency() +\
                                               self.alu_list[0].getLatency() +\
                                               self.xb_outMem_list[0].getLatency())

            latency_unit2 = latency_unit2 * np.ceil(float(self.de_xb_nma)/param.num_adc)

            latency_unit = max (latency_unit1, latency_unit2)
            latency_out = (param.xbdata_width / param.dac_res + 1) * latency_unit #might need correction !!

            return latency_out


        # State machine runs only if the stage is non-empty
        # Describe the functionality on a cycle basis
        if (self.stage_empty[sId] != 1):
            # First cycle - update the target latency
            if (self.stage_cycle[sId] == 0):
                # Check for assertion pass
                ex_op = self.de_opcode
                assert (ex_op in param.op_list), 'unsupported opcode'

                # assign execution unit based stage latency
                if (ex_op in ['ld', 'st']):
                    self.stage_latency[sId] = self.mem_interface.getLatency() #mem_interface has infinite latency
                    if (ex_op == 'ld'):
                        self.mem_interface.rdRequest (self.de_addr)
                    elif (ex_op == 'st'):
                        ramstore = str(self.de_val2) + self.de_val1
                        self.mem_interface.wrRequest (self.de_addr, ramstore)

                elif (ex_op == 'alu' or ex_op == 'alui'):
                    # ALU instructions access ALU and write to memory
                    self.stage_latency[sId] = self.alu_list[0].getLatency() +\
                                              self.dataMem.getLatency()
                elif (ex_op == 'mvm'):
                    self.stage_latency[sId] = xbComputeLatency (self)
                else: # halt instruction
                    self.stage_latency[sId] = 1

                # Check if first = last cycle - NA for LD/ST
                if (self.stage_latency[sId] == 1 and update_ready):
                    do_execute (self, ex_op, fid)
                    self.stage_done[sId] = 1
                    self.stage_cycle[sId] = 0
                    self.stage_empty[sId] = 1
                else: # NA for LD/ST
                    self.stage_cycle[sId] = self.stage_cycle[sId] + 1

            # Last cycle - update pipeline registers (if ??) & done flag - or condition is for LD/ST
            elif ((self.stage_cycle[sId] >= self.stage_latency[sId]-1 and update_ready) or \
                  (self.de_opcode == 'st' and self.mem_interface.wait == 0 and update_ready)): # ST finishes when mem access is done
                ex_op = self.de_opcode
                do_execute (self, ex_op, fid)
                self.stage_done[sId] = 1
                self.stage_cycle[sId] = 0
                self.stage_empty[sId] = 1

            # For all other cycles
            else:
                # Assumption - DataMemory cannot be done in the last edram access cycle
                if (self.de_opcode == 'ld' and self.mem_interface.wait == 0 and self.ldAccess_done == 0): # LD finishes after mem_access + reg_write is done
                    self.ldAccess_done = 1
                    self.stage_cycle[sId] = self.stage_latency[sId] - self.dataMem.getLatency () # can be data_mem too
                else:
                    self.stage_cycle[sId] = self.stage_cycle[sId] + 1


    #####################################################
    ## Define how pipeline executes
    #####################################################
    def pipe_init (self, instrn_filepath, fid = ''):
        self.debug = 0
        # tracefile stores the debug trace in debug mode
        if (param.debug and (fid != '')):
            self.debug = 1
            fid.write ('Cycle information is printed is at the end of the clock cycle\n')
            fid.write ('Assumption: A clock cycle ends at the positive edge\n')

        self.halt = 0

        zero_list = [0] * self.num_stage
        one_list = [1] * self.num_stage

        self.stage_empty = one_list[:]
        self.stage_empty[0] = 0 # fetch doesn't begin with empty
        self.stage_cycle = zero_list[:]
        self.stage_done = one_list[:]

        #Initialize the instruction memory
        dict_list = np.load(instrn_filepath)
        self.instrnMem.load(dict_list)

        self.ldAccess_done = 0

    # Mimics one cycle of ima pipeline execution
    def pipe_run (self, cycle, fid = ''): # fid is tracefile's id
        # Run the pipeline for once cycle
        # Define a stage function
        stage_function = {0 : self.fetch,
                          1 : self.decode,
                          2 : self.execute}

        # Traverse the pipeline to update the update_ready flag & execute the stages in backward order
        for i in range (self.num_stage-1, -1, -1):
            # set update_ready flag
            if (i == self.num_stage-1):
                update_ready = 1
            else:
                update_ready = self.stage_done[i+1]

            # run the stage based on its update_ready argument
            stage_function[i] (update_ready, fid)

        # If specified, print thetrace (pipeline stage information)
        if (self.debug):
            fid.write('Cycle ' + str(cycle) + '\n')

            sId = 0 # Fetch
            fid.write('Fet | PC ' + str(self.pc))
            fid.write(' | Flags: empty ' + str(self.stage_empty[sId]) + ' done ' + str(self.stage_done[sId]) \
                    + ' cycles ' + str(self.stage_cycle[sId]) + '\n')

            sId = 1 # Decode
            fid.write ('Dec | Inst: ')
            json.dump (self.fd_instrn, fid)
            fid.write(' | Flags: empty ' + str(self.stage_empty[sId]) + ' done ' + str(self.stage_done[sId]) \
                    + ' cycles ' + str(self.stage_cycle[sId]) + '\n')

            sId = 2 # Execute
            fid.write('Exe | Inst: ')
            json.dump(self.de_instrn, fid)
            fid.write(' | Flags: empty ' + str(self.stage_empty[sId]) + ' done ' + str(self.stage_done[sId]) \
                    + ' cycles ' + str(self.stage_cycle[sId]) + '\n')
            fid.write('\n')

            if (self.halt == 1):
                fid.write ('IMA halted at ' + str(cycle) + ' cycles')

