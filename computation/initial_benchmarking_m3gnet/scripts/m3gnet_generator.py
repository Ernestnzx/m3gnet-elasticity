import sys

filename, temperature = sys.argv[1], int(sys.argv[2])
annealing = (temperature-300)*1000
if not filename or not temperature: 
    print(f'Usage: <filename> <temperature>')
    sys.exit(1)
# unmelted relexation at 300K under NVT and NPT ensemble at 0 bars of pressure
relax_script = f"""# The relevant units for metal is as follows:
# - mass = grams/mol
# - distance = Angstroms
# - time = picoseconds
# - energy = eV
# - velocity = Angstroms/picosecond
# - temperature = Kelvin
# - pressure = bars
# - density = gram/cm^dim

units           metal
dimension       3
boundary        p p p
atom_style      atomic
timestep        0.001   # 1 femtosecond

variable thermal_damp index 10.0
variable pressure_damp index 100.0

read_data       ../../structures/dat/{filename}.dat
pair_style      m3gnet/gpu ../../potentials/M3GNET 
pair_coeff      * * M3GNet-MP-2021.2.8-DIRECT-PES {'Si O' if filename == "333SiO2-1-UFF" else 'Si H C O'}
dump            atom_pos all custom 100 ../outputs/unmelted_traj/unmelted_{filename}.lammpstrj element x y z
dump_modify     atom_pos element {'Si O' if filename == "333SiO2-1-UFF" else 'Si H C O'}
log             ../outputs/log_files/unmelted/unmelted_{filename}.log

# Thermodynamic output
thermo          1000
thermo_style    custom step temp pe ke etotal press vol density

# Step 1: Initial minimization + NVT & NPT relaxations at 300 Kelvin
minimize        1.0e-10 1.0e-10 100000 100000
velocity all create 300.0 12345 mom yes rot yes dist gaussian

neighbor 2.0 bin
fix nvt_relax   all nvt/gpu temp 300 300 ${{thermal_damp}}
run 100000      # 100 picoseconds
unfix           nvt_relax

fix npt_relax   all npt/gpu temp 300 300 ${{thermal_damp}} iso 0 0 ${{pressure_damp}}
run 100000      # 100 picoseconds
unfix           npt_relax

write_restart   ../structures/unmelted/unmelted_{filename}.restart
"""
with open(f"../inputs/unmelted/input_{filename}.lammps", 'w') as file:
    file.write(relax_script)

# Heating up the material from 300K to the temperature specified by the user
melting_script = f"""
# - mass = grams/mol
# - distance = Angstroms
# - time = picoseconds
# - energy = eV
# - velocity = Angstroms/picosecond
# - temperature = Kelvin
# - pressure = bars
# - density = gram/cm^dim

units           metal
dimension       3
boundary        p p p
atom_style      atomic
timestep        0.001   # 1 femtosecond

variable thermal_damp index 10.0
variable pressure_damp index 1000.0

read_restart    ../structures/unmelted/unmelted_{filename}.restart
pair_style      m3gnet/gpu ../../potentials/M3GNET 
pair_coeff      * * M3GNet-MP-2021.2.8-DIRECT-PES {'Si O' if filename == "333SiO2-1-UFF" else 'Si H C O'}
dump            melting all custom 100 ../outputs/melted_traj/melted_{filename}_{temperature}.lammpstrj element x y z
dump_modify     melting element {'Si O' if filename == "333SiO2-1-UFF" else 'Si H C O'}
log             ../outputs/log_files/melted/melted_{filename}_{temperature}.log
neighbor 2.0 bin

# Thermodynamic output
thermo          1000
thermo_style    custom step temp pe ke etotal press vol density

fix nvt_heat    all nvt/gpu temp 300 {temperature} ${{thermal_damp}}
run 100000      # 100 picoseconds 
unfix           nvt_heat

fix npt_heat    all npt/gpu temp {temperature} {temperature} ${{thermal_damp}} iso 0 0 ${{pressure_damp}}
run 100000      # 100 picoseconds
unfix           npt_heat

write_restart ../structures/melted/melted_{filename}_{temperature}.restart
"""
with open(f"../inputs/melted/input_{filename}_{temperature}.lammps", 'w') as file:
    file.write(melting_script)

# Annealing the material from the specifed temperature under NPT and relaxation at 300K under NPT
annealed_script = f"""
# - mass = grams/mol
# - distance = Angstroms
# - time = picoseconds
# - energy = eV
# - velocity = Angstroms/picosecond
# - temperature = Kelvin
# - pressure = bars
# - density = gram/cm^dim

units           metal
dimension       3
boundary        p p p
atom_style      atomic
timestep        0.001   # 1 femtosecond

variable thermal_damp index 10.0
variable pressure_damp index 1000.0

read_restart    ../structures/melted/melted_{filename}_{temperature}.restart
pair_style      m3gnet/gpu ../../potentials/M3GNET 
pair_coeff      * * M3GNet-MP-2021.2.8-DIRECT-PES {'Si O' if filename == "333SiO2-1-UFF" else 'Si H C O'}
dump            melting all custom 1000 ../outputs/annealed_traj/annealed_{filename}_{temperature}.lammpstrj element x y z
dump_modify     melting element {'Si O' if filename == "333SiO2-1-UFF" else 'Si H C O'}
log             ../outputs/log_files/annealed/annealed_{filename}_{temperature}.log
neighbor 2.0 bin

# Thermodynamic output
thermo          1000
thermo_style    custom step temp pe ke etotal press vol density

fix cooling_npt all npt/gpu temp {temperature} 300 ${{thermal_damp}} iso 0 0 ${{pressure_damp}}
run             {annealing}
unfix           cooling_npt

# Step 4: Final relaxation 
fix npt_final   all npt/gpu temp 300 300 ${{thermal_damp}} iso 0 0 100
run 100000      # 100 picoseconds
unfix           npt_final

write_restart ../structures/annealed/annealed_{filename}_{temperature}.restart
"""
with open(f"../inputs/annealed/input_{filename}_{temperature}.lammps", 'w') as file:
    file.write(annealed_script)

# Deformation of the material under adiabatic conditions
deformation_script = f"""
# - mass = grams/mol
# - distance = Angstroms
# - time = picoseconds
# - energy = eV
# - velocity = Angstroms/picosecond
# - temperature = Kelvin
# - pressure = bars
# - density = gram/cm^dim

variable up equal 2.0e-2
 
# metal units, elastic constants in GPa
units		metal
variable cfac equal 1.0e-4
variable cunits string GPa

# Define MD parameters
variable nevery equal 10                        # sampling interval
variable nrepeat equal 10                       # number of samples
variable nfreq equal ${{nevery}}*${{nrepeat}}       # length of one average
variable nthermo equal ${{nfreq}}                 # interval for thermo output
variable nequil equal 10*${{nthermo}}             # length of equilibration run
variable nrun equal 3*${{nthermo}}                # length of equilibrated run
variable temp equal 300.0                       # temperature of initial sample
variable timestep equal 0.001                   # timestep
variable adiabatic equal 0                      # adiabatic (1) or isothermal (2)
variable tdamp equal 0.01                       # time constant for thermostat
variable seed equal 123457                      # seed for thermostat

read_restart ../structures/annealed/annealed_{filename}_{temperature}.restart
log ../outputs/log_files/deformation/deformation_{filename}_{temperature}.log

pair_style      m3gnet/gpu ../../potentials/M3GNET 
pair_coeff      * * M3GNet-MP-2021.2.8-DIRECT-PES {'Si O' if filename == "333SiO2-1-UFF" else 'Si H C O'}
thermo          1000
thermo_style    custom step temp pe ke etotal press vol density
fix npt_equil   all npt/gpu temp 300 300 10.0 iso 0 0 100
run 50000       # 50 picoseconds
unfix           npt_equil

variable thermostat equal 1
include ../inputs/deformation/potential_{filename}.mod
run ${{nequil}}

if "${{adiabatic}} == 1" &
then "variable thermostat equal 0" &
else "variable thermostat equal 1"

include ../inputs/deformation/potential_{filename}.mod
run ${{nrun}}

variable pxx0 equal f_avp[1]
variable pyy0 equal f_avp[2]
variable pzz0 equal f_avp[3]
variable pxy0 equal f_avp[4]
variable pxz0 equal f_avp[5]
variable pyz0 equal f_avp[6]

variable tmp equal lx
variable lx0 equal ${{tmp}}
variable tmp equal ly
variable ly0 equal ${{tmp}}
variable tmp equal lz
variable lz0 equal ${{tmp}}

# These formulas define the derivatives w.r.t. strain components
# Constants uses $, variables use v_ 
variable d1 equal -(v_pxx1-${{pxx0}})/(v_delta/v_len0)*${{cfac}}
variable d2 equal -(v_pyy1-${{pyy0}})/(v_delta/v_len0)*${{cfac}}
variable d3 equal -(v_pzz1-${{pzz0}})/(v_delta/v_len0)*${{cfac}}
variable d4 equal -(v_pyz1-${{pyz0}})/(v_delta/v_len0)*${{cfac}}
variable d5 equal -(v_pxz1-${{pxz0}})/(v_delta/v_len0)*${{cfac}}
variable d6 equal -(v_pxy1-${{pxy0}})/(v_delta/v_len0)*${{cfac}}

# Write restart
write_restart restart_{filename}.equil

# uxx Perturbation
variable dir equal 1
include ../inputs/deformation/displace_{filename}.mod

# uyy Perturbation
variable dir equal 2
include ../inputs/deformation/displace_{filename}.mod

# uzz Perturbation
variable dir equal 3
include ../inputs/deformation/displace_{filename}.mod

# uyz Perturbation
variable dir equal 4
include ../inputs/deformation/displace_{filename}.mod

# uxz Perturbation
variable dir equal 5
include ../inputs/deformation/displace_{filename}.mod

# uxy Perturbation
variable dir equal 6
include ../inputs/deformation/displace_{filename}.mod

# Output final values
variable C11all equal ${{C11}}
variable C22all equal ${{C22}}
variable C33all equal ${{C33}}

variable C12all equal 0.5*(${{C12}}+${{C21}})
variable C13all equal 0.5*(${{C13}}+${{C31}})
variable C23all equal 0.5*(${{C23}}+${{C32}})

variable C44all equal ${{C44}}
variable C55all equal ${{C55}}
variable C66all equal ${{C66}}

variable C14all equal 0.5*(${{C14}}+${{C41}})
variable C15all equal 0.5*(${{C15}}+${{C51}})
variable C16all equal 0.5*(${{C16}}+${{C61}})

variable C24all equal 0.5*(${{C24}}+${{C42}})
variable C25all equal 0.5*(${{C25}}+${{C52}})
variable C26all equal 0.5*(${{C26}}+${{C62}})

variable C34all equal 0.5*(${{C34}}+${{C43}})
variable C35all equal 0.5*(${{C35}}+${{C53}})
variable C36all equal 0.5*(${{C36}}+${{C63}})

variable C45all equal 0.5*(${{C45}}+${{C54}})
variable C46all equal 0.5*(${{C46}}+${{C64}})
variable C56all equal 0.5*(${{C56}}+${{C65}})

# Average moduli for cubic crystals

variable C11cubic equal (${{C11all}}+${{C22all}}+${{C33all}})/3.0
variable C12cubic equal (${{C12all}}+${{C13all}}+${{C23all}})/3.0
variable C44cubic equal (${{C44all}}+${{C55all}}+${{C66all}})/3.0

variable bulkmodulus equal (${{C11cubic}}+2*${{C12cubic}})/3.0
variable shearmodulus1 equal ${{C44cubic}}
variable shearmodulus2 equal (${{C11cubic}}-${{C12cubic}})/2.0
variable poissonratio equal 1.0/(1.0+${{C11cubic}}/${{C12cubic}})

print "Elastic Constant 1 1 = ${{C11all}}"
print "Elastic Constant 2 2 = ${{C22all}}"
print "Elastic Constant 3 3 = ${{C33all}}"

print "Elastic Constant 1 2 = ${{C12all}}"
print "Elastic Constant 1 3 = ${{C13all}}"
print "Elastic Constant 2 3 = ${{C23all}}"

print "Elastic Constant 4 4 = ${{C44all}}"
print "Elastic Constant 5 5 = ${{C55all}}"
print "Elastic Constant 6 6 = ${{C66all}}"

print "Elastic Constant 1 4 = ${{C14all}}"
print "Elastic Constant 1 5 = ${{C15all}}"
print "Elastic Constant 1 6 = ${{C16all}}"

print "Elastic Constant 2 4 = ${{C24all}}"
print "Elastic Constant 2 5 = ${{C25all}}"
print "Elastic Constant 2 6 = ${{C26all}}"

print "Elastic Constant 3 4 = ${{C34all}}"
print "Elastic Constant 3 5 = ${{C35all}}"
print "Elastic Constant 3 6 = ${{C36all}}"

print "Elastic Constant 4 5 = ${{C45all}}"
print "Elastic Constant 4 6 = ${{C46all}}"
print "Elastic Constant 5 6 = ${{C56all}}"

print "Bulk Modulus = ${{bulkmodulus}} ${{cunits}}"
print "Shear Modulus 1 = ${{shearmodulus1}} ${{cunits}}"
print "Shear Modulus 2 = ${{shearmodulus2}} ${{cunits}}"
print "Poisson Ratio = ${{poissonratio}}"
"""
with open(f"../inputs/deformation/input_{filename}_{temperature}.lammps", 'w') as file:
    file.write(deformation_script)

# Side scripts for the Deformation calculations
potential_script = f"""
if "$(is_defined(fix,avp))" then "unfix avp"
reset_timestep 0

# Choose potential
pair_style      m3gnet/gpu ../../potentials/M3GNET 
pair_coeff      * * M3GNet-MP-2021.2.8-DIRECT-PES {'Si O' if filename == "333SiO2-1-UFF" else 'Si H C O'}

# Setup neighbor style
neighbor 1.0 nsq
neigh_modify once no every 1 delay 0 check yes

# Setup output

fix avp all ave/time  ${{nevery}} ${{nrepeat}} ${{nfreq}} c_thermo_press mode vector
thermo		${{nthermo}}
thermo_style custom step temp pe press f_avp[1] f_avp[2] f_avp[3] f_avp[4] f_avp[5] f_avp[6]
thermo_modify norm no

# Setup MD
timestep ${{timestep}}
fix 4 all nve
if "${{thermostat}} == 1" then & 
	"fix 5 all langevin ${{temp}} ${{temp}} ${{tdamp}} ${{seed}}"
"""
with open(f"../inputs/deformation/potential_{filename}.mod", 'w') as file:
    file.write(potential_script)

displacement_script = f"""
if "${{dir}} == 1" then & 
	"variable len0 equal ${{lx0}}" 
if "${{dir}} == 2" then & 
	"variable len0 equal ${{ly0}}" 
if "${{dir}} == 3" then &
	"variable len0 equal ${{lz0}}" 
if "${{dir}} == 4" then &
	"variable len0 equal ${{lz0}}" 
if "${{dir}} == 5" then &
	"variable len0 equal ${{lz0}}" 
if "${{dir}} == 6" then &
	"variable len0 equal ${{ly0}}" 

# Reset box and simulation parameters

clear
box tilt large
read_restart restart_{filename}.equil
include ../inputs/deformation/potential_{filename}.mod

# Negative deformation
variable delta equal -${{up}}*${{len0}}
variable deltaxy equal -${{up}}*xy
variable deltaxz equal -${{up}}*xz
variable deltayz equal -${{up}}*yz
if "${{dir}} == 1" then &
	"change_box all x delta 0 ${{delta}} xy delta ${{deltaxy}} xz delta ${{deltaxz}} remap units box"
if "${{dir}} == 2" then &
	"change_box all y delta 0 ${{delta}} yz delta ${{deltayz}} remap units box"
if "${{dir}} == 3" then &
	"change_box all z delta 0 ${{delta}} remap units box"
if "${{dir}} == 4" then &
	"change_box all yz delta ${{delta}} remap units box"
if "${{dir}} == 5" then &
	"change_box all xz delta ${{delta}} remap units box"
if "${{dir}} == 6" then &
	"change_box all xy delta ${{delta}} remap units box"

# Run MD
run ${{nequil}}
include ../inputs/deformation/potential_{filename}.mod
run ${{nrun}}

# Obtain new stress tensor
variable pxx1 equal f_avp[1]
variable pyy1 equal f_avp[2]
variable pzz1 equal f_avp[3]
variable pxy1 equal f_avp[4]
variable pxz1 equal f_avp[5]
variable pyz1 equal f_avp[6]

# Compute elastic constant from pressure tensor
variable C1neg equal ${{d1}}
variable C2neg equal ${{d2}}
variable C3neg equal ${{d3}}
variable C4neg equal ${{d4}}
variable C5neg equal ${{d5}}
variable C6neg equal ${{d6}}

# Reset box and simulation parameters
clear
box tilt large
read_restart restart_{filename}.equil
include ../inputs/deformation/potential_{filename}.mod

# Positive deformation

variable delta equal ${{up}}*${{len0}}
variable deltaxy equal ${{up}}*xy
variable deltaxz equal ${{up}}*xz
variable deltayz equal ${{up}}*yz
if "${{dir}} == 1" then &
	"change_box all x delta 0 ${{delta}} xy delta ${{deltaxy}} xz delta ${{deltaxz}} remap units box"
if "${{dir}} == 2" then &
	"change_box all y delta 0 ${{delta}} yz delta ${{deltayz}} remap units box"
if "${{dir}} == 3" then &
	"change_box all z delta 0 ${{delta}} remap units box"
if "${{dir}} == 4" then &
	"change_box all yz delta ${{delta}} remap units box"
if "${{dir}} == 5" then &
	"change_box all xz delta ${{delta}} remap units box"
if "${{dir}} == 6" then &
	"change_box all xy delta ${{delta}} remap units box"

# Run MD
run ${{nequil}}
include ../inputs/deformation/potential_{filename}.mod
run ${{nrun}}

# Obtain new stress tensor
variable pxx1 equal f_avp[1]
variable pyy1 equal f_avp[2]
variable pzz1 equal f_avp[3]
variable pxy1 equal f_avp[4]
variable pxz1 equal f_avp[5]
variable pyz1 equal f_avp[6]

# Compute elastic constant from pressure tensor
variable C1pos equal ${{d1}}
variable C2pos equal ${{d2}}
variable C3pos equal ${{d3}}
variable C4pos equal ${{d4}}
variable C5pos equal ${{d5}}
variable C6pos equal ${{d6}}

# Combine positive and negative 
variable C1${{dir}} equal 0.5*(${{C1neg}}+${{C1pos}})
variable C2${{dir}} equal 0.5*(${{C2neg}}+${{C2pos}})
variable C3${{dir}} equal 0.5*(${{C3neg}}+${{C3pos}})
variable C4${{dir}} equal 0.5*(${{C4neg}}+${{C4pos}})
variable C5${{dir}} equal 0.5*(${{C5neg}}+${{C5pos}})
variable C6${{dir}} equal 0.5*(${{C6neg}}+${{C6pos}})

# Delete dir to make sure it is not reused
variable dir delete
"""
with open(f"../inputs/deformation/displace_{filename}.mod", 'w') as file:
    file.write(displacement_script)
