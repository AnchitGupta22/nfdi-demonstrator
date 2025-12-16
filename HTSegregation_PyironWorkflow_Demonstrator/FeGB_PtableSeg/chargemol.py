import numpy as np
import pandas as pd

import os 

from pymatgen.core import Element, Structure

def parse_lines(flist, trigger_start, trigger_end, recursive=True):
    """
    Parses lines from a list of strings based on start and end triggers and returns the parsed data.

    Parameters:
        flist (list): A list of strings representing the lines to parse.
        trigger_start (str): The trigger string indicating the start of the data block.
        trigger_end (str): The trigger string indicating the end of the data block.
        recursive (bool, optional): Determines whether to parse recursively for multiple data blocks. Defaults to True.

    Returns:
        list: A list of parsed data blocks.

    Usage:
        # Parse lines between specific start and end triggers
        parse_lines(lines, "START", "END")

        # Parse lines between specific start and end triggers recursively
        parse_lines(lines, "START", "END", recursive=True)

        # Parse lines between specific start and end triggers without recursion
        parse_lines(lines, "START", "END", recursive=False)

    Note:
        - The function iterates over the lines in the `flist` list and identifies the data blocks based on the specified start and end triggers.
        - It returns a list of parsed data blocks, where each data block is a list of lines between a start trigger and an end trigger.
        - If `recursive` is True, the function continues parsing for multiple data blocks, even after finding an end trigger.
        - If `recursive` is False, the function stops parsing after finding the first end trigger.
        - If no data blocks are found, an empty list is returned.
    """
    parsing = False
    any_data = False
    data = []
    for line in flist:
        if trigger_end in line:
            parsing = False
            data.append(data_block)
            if not recursive:
                break
            else:
                continue
        if parsing:
            data_block.append(line)
        if trigger_start in line:
            any_data = True
            parsing = True
            data_block = []
    if not any_data:
        data = []
    if parsing and not trigger_end in line:
        data.append(data_block)

    return data

def get_unique_values_in_nth_value(arr_list, n, tolerance):
    unique_values = []
    for sublist in arr_list:
        value = sublist[n]
        is_unique = True
        for unique_value in unique_values:
            if np.allclose(value, unique_value, atol=tolerance):
                is_unique = False
                break
        if is_unique:
            unique_values.append(value)
    return np.sort(unique_values)

def compute_average_pairs(lst):
    averages = []
    for i in range(len(lst) - 1):
        average = (lst[i] + lst[i + 1]) / 2
        averages.append(average)
    return averages

class ChargemolAnalysis():
    def __init__(self, directory):
        self.directory = directory
        self._struct = None
        self._bond_matrix = None
        self.parse_DDEC6_analysis_output()
        
    def parse_DDEC6_analysis_output(self):
        struct, bond_matrix = parse_DDEC6_analysis_output(os.path.join(self.directory, "VASP_DDEC_analysis.output"))
        self.struct = struct
        self.bond_matrix = bond_matrix
        return struct, bond_matrix

    # Getter for struct attribute
    def get_struct(self):
        return self._struct

    # Setter for struct attribute
    def set_struct(self, struct):
        self._struct = struct

    # Getter for bond_matrix attribute
    def get_bond_matrix(self):
        return self._bond_matrix

    # Setter for bond_matrix attribute
    def set_bond_matrix(self, bond_matrix):
        self._bond_matrix = bond_matrix

    def get_ANSBO_profile(self, axis=2, tolerance=0.1):
        return get_ANSBO_all_cleavage_planes(self.struct, self.bond_matrix, axis=axis, tolerance=tolerance)

    def get_min_ANSBO(self, axis=2, tolerance=0.1):
        return min(get_ANSBO_all_cleavage_planes(self.struct, self.bond_matrix, axis=axis, tolerance=tolerance))
    
    def analyse_ANSBO(self, axis=2, tolerance=0.1):
        return analyse_ANSBO(self.directory, axis=axis, tolerance=tolerance)
    
def parse_DDEC6_analysis_output(filename):
    """
    Parses VASP_DDEC_analysis.output files and returns a Structure object and bond matrix.

    Args:
        filepaths (str or list): The path(s) to the DDEC6 output file(s) to be parsed.

    Returns:
        tuple: A tuple containing the Structure object and bond matrix.
            - The Structure object represents the atomic structure of the system
            and contains information about the lattice, atomic coordinates,
            and atomic numbers.
            - The bond matrix is a DataFrame that provides information about the
            bonding interactions in the system, including bond indices, bond lengths,
            and other properties.

    Raises:
        FileNotFoundError: If the specified file(s) do not exist.

    Example:
        filepaths = ["output1.txt", "output2.txt"]
        structure, bond_matrix = parse_DDEC6(filepaths)
        print(structure)
        print(bond_matrix)

    Note:
        - The function reads the specified DDEC6 output file(s) and extracts relevant
        information to create a Structure object and bond matrix.
        - The function expects the DDEC6 output files to be in a specific format and
        relies on certain trigger lines to identify the relevant sections.
        - The structure lattice is parsed from the lines between the "vectors" and
        "direct_coords" triggers.
        - The atomic fractional coordinates are parsed from the lines between the
        "direct_coords" and "totnumA" triggers.
        - The atomic numbers are parsed from the lines between the "(Missing core
        electrons will be inserted using stored core electron reference densities.)"
        and "Finished the check for missing core electrons." triggers.
        - The atomic numbers are converted to element symbols using the pymatgen
        Element.from_Z() method.
        - The Structure object is created using the parsed lattice, atomic numbers,
        and fractional coordinates.
        - The bond matrix is parsed from the lines between the "The final bond pair
        matrix is" and "The legend for the bond pair matrix follows:" triggers.
        - The bond matrix is returned as a pandas DataFrame with the specified column
        names.

    """
    flist = open(filename).readlines()

    bohr_to_angstrom_conversion_factor = 0.529177
    structure_lattice = parse_lines(flist, trigger_start="vectors", trigger_end="direct_coords")[0]
    structure_lattice = np.array([list(map(float, line.split())) for line in structure_lattice])
    structure_lattice = structure_lattice * bohr_to_angstrom_conversion_factor

    structure_frac_coords = parse_lines(flist, trigger_start="direct_coords", trigger_end="totnumA")[0]
    structure_frac_coords = [np.array([float(coord) for coord in entry.split()]) for entry in structure_frac_coords]

    # Convert atomic numbers to element symbols
    structure_atomic_no = parse_lines(flist, trigger_start="(Missing core electrons will be inserted using stored core electron reference densities.)", trigger_end=" Finished the check for missing core electrons.")
    structure_atomic_no = [Element.from_Z(int(atomic_number.split()[1])).symbol for atomic_number in structure_atomic_no[0]]

    structure = Structure(structure_lattice, structure_atomic_no, structure_frac_coords)

    data_column_names = ['atom1',\
                'atom2',\
                'repeata',\
                'repeatb',\
                'repeatc',\
                'min-na',\
                'max-na',\
                'min-nb',\
                'max-nb',\
                'min-nc',\
                'max-nc',\
                'contact-exchange',\
                'avg-spin-pol-bonding-term',\
                'overlap-population',\
                'isoaepfcbo',\
                'coord-term-tanh',\
                'pairwise-term',\
                'exp-term-comb-coord-pairwise',\
                'bond-idx-before-self-exch',\
                'final_bond_order']

    bond_matrix = parse_lines(flist, trigger_start="The final bond pair matrix is", trigger_end="The legend for the bond pair matrix follows:")[0]
    bond_matrix = np.array([list(map(float, line.split())) for line in bond_matrix])
    bond_matrix = pd.DataFrame(bond_matrix, columns=data_column_names)

    return structure, bond_matrix

def analyse_ANSBO(directory, axis=2, tolerance=0.1):
    """
    
    """
    struct, bond_matrix = parse_DDEC6_analysis_output(os.path.join(directory, "VASP_DDEC_analysis.output"))
    atomic_layers = get_unique_values_in_nth_value(struct.cart_coords, axis, tolerance = tolerance)
    cp_list = compute_average_pairs(atomic_layers)
    ANSBO_profile = get_ANSBO_all_cleavage_planes(struct, bond_matrix, axis=axis, tolerance=tolerance)
    
    results_dict = {"layer_boundaries": atomic_layers,
                    "cleavage_coord": cp_list,
                    "ANSBO_profile": ANSBO_profile}
    return results_dict

def get_ANSBO_all_cleavage_planes(structure, bond_matrix, axis = 2, tolerance = 0.1):
    atomic_layers = get_unique_values_in_nth_value(structure.cart_coords, axis, tolerance = tolerance)
    cp_list = compute_average_pairs(atomic_layers)

    ANSBO_profile = []
    for cp in cp_list:
        ANSBO_profile.append(get_ANSBO(structure, bond_matrix, cp))
    return cp_list, ANSBO_profile

def get_ANSBO(structure, bond_matrix, cleavage_plane, axis = 2):
    bond_matrix['atom1pos'] = [structure[int(x)-1].coords[axis] for x in bond_matrix['atom1'].values]
    bond_matrix['atom2pos'] = [structure[int(x)-1].coords[axis] for x in bond_matrix['atom2'].values]
    clp_df = bond_matrix[(bond_matrix[['atom1pos','atom2pos']].max(axis=1) > cleavage_plane)
                         & (bond_matrix[['atom1pos','atom2pos']].min(axis=1) < cleavage_plane) ]
    if axis == 0:
        repeat1 = "repeatb"
        repeat2 = "repeatc"
    elif axis == 1:
        repeat1 = "repeata"
        repeat2 = "repeatc"
    elif axis == 2:
        repeat1 = "repeata"
        repeat2 = "repeatb"
        
    clp_df = clp_df.copy()[(clp_df[repeat1] == 0) | (clp_df[repeat2] == 0)]
    # We only want to calculate for atoms that exist in cell. This is important for bond order/area normalisation
    clp_df_countonce = clp_df.copy()[(clp_df[repeat1] == 0) & (clp_df[repeat2] == 0)]
    clp_df_counthalf = clp_df.copy()[(clp_df[repeat1] != 0) | (clp_df[repeat2] != 0)]
    # Basic summed bond order over CP
    final_bond_order = clp_df_countonce.final_bond_order.sum() + 0.5*clp_df_counthalf.final_bond_order.sum()
    # N largest
    #final_bond_order = clp_df.nlargest(15, ['final_bond_order'])["final_bond_order"].sum()
    # IMPORTANT: This assumes that the cross sectional area can be calculated this way
    a_fbo = final_bond_order/(float(structure.lattice.volume)/float(structure.lattice.abc[axis]))
    #print("area of this is %s" % (float(structure.lattice.volume)/float(structure.lattice.c)))
    return a_fbo