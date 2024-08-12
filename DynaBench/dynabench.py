import argparse
import DynaBench.dynabench as dynabench
import DynaBench.Plots as Plots
import json
import time
from datetime import datetime
import warnings
import ContactMatrix
import Betweenness
warnings.filterwarnings('ignore')

def print_dynabench():
    db_dict = {
    'A': ['  A  ', ' A A ', 'AAAAA', 'A   A', 'A   A'],
    'B': ['BBBB ', 'B   B', 'BBBB ', 'B   B', 'BBBB '],
    'C': [' CCC ', 'C   C', 'C    ', 'C   C', ' CCC '],
    'D': ['DDDD ', 'D   D', 'D   D', 'D   D', 'DDDD '],
    'E': ['EEEEE', 'E    ', 'EEEEE', 'E    ', 'EEEEE'],
    'H': ['H   H', 'H   H', 'HHHHH', 'H   H', 'H   H'],
    'N': ['N   N', 'NN  N', 'N N N', 'N  NN', 'N   N'],
    'Y': ['Y   Y', ' Y Y ', '  Y  ', '  Y  ', '  Y  '],
}

    word = "DYNABENCH"

    for i in range(5):
        for w in word:
            print(db_dict[w][i], end='  ')
        print()


def print_stars(r):
    for i in range(r):
        for j in range(40):
            if (i + j) % 3 == 0:
                print("★", end=' ')
            else:
                print("☆", end=' ')
        print()




parser = argparse.ArgumentParser()


#required?
parser.add_argument('-ip', '--input_file', type=str, help="Input File in .dcd or .pfb formats. If .dcd, pelase provide .pdb file with '--dcd_pdb' command.")
parser.add_argument('-c', '--commands', type=str, help="Commands to run. You can provide multiple run commands, in comma seperated form. Choises are:\n'all_analysis', 'QualityControl', 'ResidueBased', 'InteractionBased' for analysis and,\n 'all_plots', 'PlotRMSD', 'PlotRG', 'PlotRMSF', 'PlotPairwiseFreq', 'PlotBiophys', 'PlotResEne', ' for visualization.") #virgül seperated al, kontrol et

#job_name
parser.add_argument('-j', '--job_name', type=str, help='The name of the job, if null, DynaBench will generate a name from input file.')
#tables
parser.add_argument('--foldx_path', type=str)
parser.add_argument('--time_as', type=str, help="'Frame' or 'Time'. If Time, you should provide time unit with --timeunit command.")
parser.add_argument('--timestep', type=str, help="Timestep value of simulation.")
parser.add_argument('--timeunit', type=str, help="Nanosecond or ns is acceptable for now.")
parser.add_argument('--dcd_pdb', type=str, help="Path of pdb file for dcd inputs.")
parser.add_argument('-s', '--stride', type=int, help="Stride value.")
parser.add_argument('-sm', '--split_models', type=bool, help="Whether models will be splitted or not.")
parser.add_argument('-ch', '--chains', type=str, help="For heteromers, you can decide which two chains to be analyzed. Provide input such as 'A,B'.")
parser.add_argument('--rmsd_rs', type=str, help="Path to reference structure for RMSD analyse.") #rmsd_ref_struc
parser.add_argument('--rmsd_rf', type=int, help="Reference frame for RMSD analyze.") #rmsd_ref_frame
parser.add_argument('--all_hph', type=bool, help="You can decide whether all possible hydrophobic bond will be calculated or not.") #get_all_hph
#plots
parser.add_argument('--rmsd_tpath', type=str, help="CSV data path for RMSD plot.") #rmsd draw table path
parser.add_argument('--rg_tpath', type=str, help="CSV data path for RG plot.") #rg draw table path
parser.add_argument('--rmsf_tpath', type=str, help="CSV data path for RMSF plot.") #rmsf draw table path
parser.add_argument('--rmsf_itpath', type=str, help="CSV data including interface residues path for RMSF plot.") #rmsf draw interface res. path
parser.add_argument('--biophy_tpath', type=str, help="CSV data path of residue based analyse.") #biophysical type draw table path 
parser.add_argument('--bondfreq_tpath', type=str, help="CSV data of interaction based analyse.") #bondfreq draw table path
parser.add_argument('--int_ene_itpath', type=str, help="CSV data path of residue based analyse.") #interaction energy draw interface res. path
parser.add_argument('--int_ene_tpath', type=str, help="CSV data including interface residues path for interaction energy plot.") #interaction energy draw table path
parser.add_argument('--bet_cent_path', type=str, help="CSV data of nodes with 95th percentile betweenness centrality.") #interaction energy draw table path
parser.add_argument('--bet_freq_path', type=str, help="CSV data of nodes with 95th percentile betweenness centrality and their frequencies.") #interaction energy draw table path
parser.add_argument('--nodes_path', type=str, help="CSV data of top  5% nodes.") #interaction energy draw table path


parser.add_argument('--table_json', type=str, help="JSON file path for analyse runs.")
parser.add_argument('--plot_json', type=str, help="JSON file path for plot runs.")

args = parser.parse_args()

if args.commands:
    commands = args.commands.split(',')


if args.table_json:
    table_commands = []
    a_json_ = True

    f = open(args.table_json)
    table_data = json.load(f)

    if table_data['QualityControl']['Run']:
        table_commands.append('QualityControl')

    if table_data['ResidueBased']['Run']:
        table_commands.append('ResidueBased')

    if table_data['InteractionBased']['Run']:
        table_commands.append('InteractionBased')
    
else:
    a_json_ = False
    if args.commands:
        if 'all_analysis' in commands:
            table_commands = ['QualityControl', 'ResidueBased', 'InteractionBased']
        else:
            table_commands = [x for x in commands if 'plot' not in x.lower()]
    else:
        table_commands = None


if args.plot_json:
    plot_commands = []
    p_json = True

    f2 = open(args.plot_json)
    plot_data = json.load(f2)

    if plot_data['PlotRMSD']['Run']:
        plot_commands.append('PlotRMSD')
    if plot_data['PlotRG']['Run']:
        plot_commands.append('PlotRG')
    if plot_data['PlotRMSF']['Run']:
        plot_commands.append('PlotRMSF')
    if plot_data['PlotPairwiseFreq']['Run']:
        plot_commands.append('PlotPairwiseFreq')
    if plot_data['PlotBiophys']['Run']:
        plot_commands.append('PlotBiophys')
    if plot_data['PlotResEne']['Run']:
        plot_commands.append('PlotResEne')
    

else:
    p_json = False
    if args.commands:
        if 'all_plots' in commands:
            plot_commands = ['PlotRMSD', 'PlotRG', 'PlotRMSF', 'PlotPairwiseFreq', 'PlotBiophys', 'PlotResEne']
        else:
            plot_commands = [x for x in commands if 'plot' in x.lower()]
    else:
        plot_commands = None
    
def main():
    print("\n")
    print_stars(1)
    print_dynabench()
    print_stars(1)
    #print("   Generated by Karaca Lab, IBG")
    print("\n")
    time.sleep(0.5)

    #tables
    if table_commands:

        if a_json_:
            inp_file = table_data['input_file']
            job_name = table_data['job_name']
            stride = table_data['stride']
            split_models = table_data['split_models']
            chains = table_data['chains']
            dcd_pdb = table_data['dcd_pdb']
            time_as = table_data['show_time_as']
            timestep = table_data['timestep']
            timeunit = table_data['timeunit']
            pdb_path = table_data['dcd_pdb'] ##bak
            dcd_path = table_data['input_file']## bak
            

        else:
            inp_file = args.input_file
            job_name = args.job_name
            stride = args.stride
            split_models = args.split_models
            chains = args.chains
            dcd_pdb = args.dcd_pdb
            time_as = args.time_as
            timestep = args.timestep
            timeunit = args.timeunit
            pdb_path = args.dcd_pdb
            dcd_path = args.input_file
        
        if not stride:
            stride = 1
        if not split_models:
            split_models=False
        if not timestep:
            timestep=1.0

        print('Creating DynaBench class...\n')

        mol = dynabench(inp_file=inp_file, stride=stride, split_models=split_models, chains=chains, job_name=job_name, dcd_pdb=dcd_pdb,
                        show_time_as=time_as, timestep=timestep, time_unit=timeunit)

        print(f'Your DynaBench Class has been created with the following parameters:\n\tJob Name:{mol.job_name}\n\tInput File: {inp_file}\n\tDCD-related PDB: {dcd_pdb}\n\tStride: {stride}\n\tSplit Models: {split_models}\n\tChain Selection: {chains}\n')
        print_stars(1)
        print("\n")


     # Run Contact matrix
        print("Running ContactMatrix.py...")
        ContactMatrix.run_ContactMatrix(pdb_path, dcd_path, stride)
        print("ContactMatrix.py has been executed.\n")
        print_stars(1)
        print("\n")

    # Run Betweenness
        print("Running Betweenness.py...")
        Betweenness.calculate_betweenness(contact_matrix_file, output_path="output")
        print("Betweenness.py has been executed.\n")
        print_stars(1)
        print("\n")



        if 'QualityControl' in table_commands:

            if a_json_:
                rmsd_rs = table_data['QualityControl']['rmsd_data']['ref_struc']
                rmsd_rf = table_data['QualityControl']['rmsd_data']['ref_frame']

            else:
                rmsd_rs = args.rmsd_rs
                rmsd_rf = args.rmsd_rf

            if not rmsd_rf:
                rmsd_rf = 0

            print('Running Quality Control Analysis...\n')
            start_time = datetime.now()
            mol.run_quality_control(rmsd_data={'ref_struc':rmsd_rs, 'ref_frame':rmsd_rf})
            end_time = datetime.now()
            print(f"Quality Control Analysis has run successfully!\nRunning duration: {end_time - start_time}\n") #time ekle
            print_stars(1)
            print("\n")
        if 'ResidueBased' in table_commands:

            if a_json_:
                foldx_path = table_data['ResidueBased']['FoldX_path']
            else:
                foldx_path = args.foldx_path
            
            print('Running Residue Based Analysis...\n')
            start_time = datetime.now()
            mol.run_res_based(foldx_path)
            end_time = datetime.now()
            print(f"Residue Based Analysis has run successfully!\nRunning duration: {end_time - start_time}\n")
            print_stars(1)
            print("\n")

        if 'InteractionBased' in table_commands:

            if a_json_:
                all_hph = table_data['InteractionBased']['get_all_hph']

            else:
                all_hph = args.all_hph
            
            if not all_hph:
                all_hph = False
            
            print('Running Interaction Based Analysis... Running Interaction Analyze may take several minutes to hours, based on your input.\n')
            start_time = datetime.now()
            mol.run_inter_based(get_all_hph=all_hph)
            end_time = datetime.now()
            print(f"Interaction Based Analysis has run successfully!\nRunning duration: {end_time - start_time}\n")
            print_stars(1)
            print("\n")

        if not a_json_:
            mol._get_params_()
            print("Your table run parameters are downloaded as table_params.json")
        else:
            f.close()

    #plots
    if plot_commands:
        if p_json:
            job_name = plot_data['job_name']
        else:
            job_name = args.job_name

        print_stars(1)
        print("\n")
        draw = Plots.Plotter(job_name=job_name)
        print(f'Your Plotter Class has been created\n')

        print_stars(1)
        print("\n")

        print('Your plots are processing...\n')
        print_stars(1)
        print("\n")

        if 'PlotRMSD' in plot_commands:
            
            if p_json:
                rmsd_tpath = plot_data['PlotRMSD']['rmsd_table_path']
                
            else:
                rmsd_tpath = args.rmsd_tpath

            draw.plot_rmsd(path=rmsd_tpath)
            print('RMSD plot is done!\n')
            print_stars(1)
            print("\n")

        if 'PlotRG' in plot_commands:
            
            if p_json:
                rg_tpath = plot_data['PlotRG']['rg_table_path']
            else:
                rg_tpath = args.rg_tpath

            draw.plot_rg(path=rg_tpath)
            print('RG plot is done!\n')
            print_stars(1)
            print("\n")
            
        if 'PlotRMSF' in plot_commands:

            if p_json:
                rmsf_tpath = plot_data['PlotRMSF']['rmsf_table_path']
                rmsf_itpath = plot_data['PlotRMSF']['rmsf_intf_res_table']
            else:
                rmsf_tpath = args.rmsf_tpath
                rmsf_itpath = args.rmsf_itpath

            draw.plot_rmsf(rmsf_path=rmsf_tpath, intf_path=rmsf_itpath)
            print('RMSF plot is done!\n')
            print_stars(1)
            print("\n")
        
        if 'PlotBiophys' in plot_commands:

            if p_json:
                biophys_tpath = plot_data['PlotBiophys']['biophys_table_path']
                biophys_palette = plot_data['PlotBiophys']['biophys_palette']

                if biophys_palette:
                    draw._biophys_palette = biophys_palette
            else:
                biophys_tpath = args.biophy_tpath
            
            draw.plot_biophys(path=biophys_tpath)
            print('Biophysical Type plot is done!\n')
            print_stars(1)
            print("\n")

        if

        if 'PlotPairwiseFreq' in plot_commands:

            if p_json:
                bondfreq_tpath = plot_data['PlotPairwiseFreq']['bar_table_path']
                bondfreq_palette = plot_data['PlotPairwiseFreq']['bar_palette']

                if bondfreq_palette:
                    draw._bar_palette = bondfreq_palette

            else:
                bondfreq_tpath = args.bondfreq_tpath

            draw.plot_pairwise_freq(path=bondfreq_tpath)
            print('Bond Frequencies Bar Plot is done!\n')
            print_stars(1)
            print("\n")

        if 'PlotResEne' in plot_commands:
            int_ene_thr = 50.0

            if p_json:
                int_ene_thr = plot_data['PlotResEne']['interface_th']
                int_ene_itpath = plot_data['PlotResEne']['interface_table_path']
                int_ene_tpath = plot_data['PlotResEne']['residue_based_table']

                

            else:
                int_ene_itpath = args.int_ene_itpath
                int_ene_tpath = args.int_ene_tpath

            draw.plot_int_energy(thereshold=int_ene_thr, intf_path=int_ene_itpath, res_path=int_ene_tpath)
            print('Interface Residue Energies Boxplot is done!\n')
            print_stars(1)
            print("\n")

        if not p_json:
            draw._get_params_()
            print("Your plot run parameters are downloaded as plot_params.json")
        else:
            f2.close()

if __name__ == '__main__':
    main()


