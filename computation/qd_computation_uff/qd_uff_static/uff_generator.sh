#!/bin/bash
if [[ $# -ne 1 ]]; then
    echo "Usage: ./uff_generator.sh <filename>"
    exit 1
fi

filename=$1
cif_file="./cif/${filename}.cif"

# Generating the base lammps data file and input script
lammps-interface --cutoff 5.0 --molecule-ff UFF ${cif_file}

#############################################################
# Appending the simulation script to the back of input file #
#############################################################
cat << \EOF >> in.${filename}
dump            atom_pos all custom 100 ./output/FILENAME.lammpstrj element x y z
thermo          1000
thermo_style    custom step temp pe ke etotal press vol density

variable up equal 2e-2
variable cfac equal 1.0e-4
variable cunits string GPa

# Define minimization parameters
variable etol equal 0.0 
variable ftol equal 1.0e-10
variable maxiter equal 100000
variable maxeval equal 100000
variable dmax equal 1.0e-2

variable temp equal 300.0
variable thermal_damp index 100.0
variable pressure_damp index 500.0

fix relax all box/relax aniso 0.0 vmax 0.001
unfix relax
minimize ${etol} ${ftol} ${maxiter} ${maxeval}

# fix npt_relax all npt temp ${temp} ${temp} ${thermal_damp} iso 0 0 ${pressure_damp}
# run 200000
# unfix npt_relax
# undump atom_pos

# density computation
# variable rho equal density   
# fix integrate  all npt temp ${temp} ${temp} ${thermal_damp} iso 0 0 ${pressure_damp}
# fix rho50k all ave/time 10 5000 50000 v_rho mode scalar ave one
# run 50000
# unfix integrate
# unfix rho50k

# Compute initial state
fix 3 all box/relax  aniso 0.0
minimize ${etol} ${ftol} ${maxiter} ${maxeval}

variable tmp equal pxx
variable pxx0 equal ${tmp}
variable tmp equal pyy
variable pyy0 equal ${tmp}
variable tmp equal pzz
variable pzz0 equal ${tmp}
variable tmp equal pyz
variable pyz0 equal ${tmp}
variable tmp equal pxz
variable pxz0 equal ${tmp}
variable tmp equal pxy
variable pxy0 equal ${tmp}

variable tmp equal lx
variable lx0 equal ${tmp}
variable tmp equal ly
variable ly0 equal ${tmp}
variable tmp equal lz
variable lz0 equal ${tmp}

# These formulas define the derivatives w.r.t. strain components
# Constants uses $, variables use v_ 
variable d1 equal -(v_pxx1-${pxx0})/(v_delta/v_len0)*${cfac}
variable d2 equal -(v_pyy1-${pyy0})/(v_delta/v_len0)*${cfac}
variable d3 equal -(v_pzz1-${pzz0})/(v_delta/v_len0)*${cfac}
variable d4 equal -(v_pyz1-${pyz0})/(v_delta/v_len0)*${cfac}
variable d5 equal -(v_pxz1-${pxz0})/(v_delta/v_len0)*${cfac}
variable d6 equal -(v_pxy1-${pxy0})/(v_delta/v_len0)*${cfac}

# displace_atoms all random ${atomjiggle} ${atomjiggle} ${atomjiggle} 87287 units box

# Write restart
unfix 3
write_restart restart_FILENAME.equil

# uxx Perturbation

variable dir equal 1
include ./input/displace_FILENAME.mod

# uyy Perturbation

variable dir equal 2
include ./input/displace_FILENAME.mod

# uzz Perturbation

variable dir equal 3
include ./input/displace_FILENAME.mod

# uyz Perturbation

variable dir equal 4
include ./input/displace_FILENAME.mod

# uxz Perturbation

variable dir equal 5
include ./input/displace_FILENAME.mod

# uxy Perturbation

variable dir equal 6
include ./input/displace_FILENAME.mod

# Output final values

variable C11all equal ${C11}
variable C22all equal ${C22}
variable C33all equal ${C33}

variable C12all equal 0.5*(${C12}+${C21})
variable C13all equal 0.5*(${C13}+${C31})
variable C23all equal 0.5*(${C23}+${C32})

variable C44all equal ${C44}
variable C55all equal ${C55}
variable C66all equal ${C66}

variable C14all equal 0.5*(${C14}+${C41})
variable C15all equal 0.5*(${C15}+${C51})
variable C16all equal 0.5*(${C16}+${C61})

variable C24all equal 0.5*(${C24}+${C42})
variable C25all equal 0.5*(${C25}+${C52})
variable C26all equal 0.5*(${C26}+${C62})

variable C34all equal 0.5*(${C34}+${C43})
variable C35all equal 0.5*(${C35}+${C53})
variable C36all equal 0.5*(${C36}+${C63})

variable C45all equal 0.5*(${C45}+${C54})
variable C46all equal 0.5*(${C46}+${C64})
variable C56all equal 0.5*(${C56}+${C65})

# Average moduli for cubic crystals

variable C11cubic equal (${C11all}+${C22all}+${C33all})/3.0
variable C12cubic equal (${C12all}+${C13all}+${C23all})/3.0
variable C44cubic equal (${C44all}+${C55all}+${C66all})/3.0

variable bulkmodulus equal (${C11cubic}+2*${C12cubic})/3.0
variable shearmodulus1 equal ${C44cubic}
variable shearmodulus2 equal (${C11cubic}-${C12cubic})/2.0
variable poissonratio equal 1.0/(1.0+${C11cubic}/${C12cubic})
  
print "Elastic Constant 1 1 = ${C11all}"
print "Elastic Constant 2 2 = ${C22all}"
print "Elastic Constant 3 3 = ${C33all}"

print "Elastic Constant 1 2 = ${C12all}"
print "Elastic Constant 1 3 = ${C13all}"
print "Elastic Constant 2 3 = ${C23all}"

print "Elastic Constant 4 4 = ${C44all}"
print "Elastic Constant 5 5 = ${C55all}"
print "Elastic Constant 6 6 = ${C66all}"

print "Elastic Constant 1 4 = ${C14all}"
print "Elastic Constant 1 5 = ${C15all}"
print "Elastic Constant 1 6 = ${C16all}"

print "Elastic Constant 2 4 = ${C24all}"
print "Elastic Constant 2 5 = ${C25all}"
print "Elastic Constant 2 6 = ${C26all}"

print "Elastic Constant 3 4 = ${C34all}"
print "Elastic Constant 3 5 = ${C35all}"
print "Elastic Constant 3 6 = ${C36all}"

print "Elastic Constant 4 5 = ${C45all}"
print "Elastic Constant 4 6 = ${C46all}"
print "Elastic Constant 5 6 = ${C56all}"

print "Bulk Modulus = ${bulkmodulus} ${cunits}"
print "Shear Modulus 1 = ${shearmodulus1} ${cunits}"
print "Shear Modulus 2 = ${shearmodulus2} ${cunits}"
print "Poisson Ratio = ${poissonratio}"

variable rho equal density
print "density (g/cm^3) = ${rho}"
EOF

sed -i "1c\log ./output/log.${filename} append" in.${filename}
sed -i "s|^\(read_data[[:space:]]\+\).*|\1./dat/data.${filename}|" in.${filename}
mv data.${filename} ./dat/
mv in.${filename} ./input/

#################################################################
# Writing the file for the displacement for the given structure #
#################################################################
cat << \EOF > ./input/displace_${filename}.mod
if "${dir} == 1" then &
   "variable len0 equal ${lx0}" 
if "${dir} == 2" then &
   "variable len0 equal ${ly0}" 
if "${dir} == 3" then &
   "variable len0 equal ${lz0}" 
if "${dir} == 4" then &
   "variable len0 equal ${lz0}" 
if "${dir} == 5" then &
   "variable len0 equal ${lz0}" 
if "${dir} == 6" then &
   "variable len0 equal ${ly0}" 

# Reset box and simulation parameters

clear
box tilt large
read_restart restart_FILENAME.equil
include ./input/angles_FILENAME.mod

# Negative deformation

variable delta equal -${up}*${len0}
variable deltaxy equal -${up}*xy
variable deltaxz equal -${up}*xz
variable deltayz equal -${up}*yz
if "${dir} == 1" then &
   "change_box all x delta 0 ${delta} xy delta ${deltaxy} xz delta ${deltaxz} remap units box"
if "${dir} == 2" then &
   "change_box all y delta 0 ${delta} yz delta ${deltayz} remap units box"
if "${dir} == 3" then &
   "change_box all z delta 0 ${delta} remap units box"
if "${dir} == 4" then &
   "change_box all yz delta ${delta} remap units box"
if "${dir} == 5" then &
   "change_box all xz delta ${delta} remap units box"
if "${dir} == 6" then &
   "change_box all xy delta ${delta} remap units box"

# Relax atoms positions

minimize ${etol} ${ftol} ${maxiter} ${maxeval}

# Obtain new stress tensor
 
variable tmp equal pxx
variable pxx1 equal ${tmp}
variable tmp equal pyy
variable pyy1 equal ${tmp}
variable tmp equal pzz
variable pzz1 equal ${tmp}
variable tmp equal pxy
variable pxy1 equal ${tmp}
variable tmp equal pxz
variable pxz1 equal ${tmp}
variable tmp equal pyz
variable pyz1 equal ${tmp}

# Compute elastic constant from pressure tensor

variable C1neg equal ${d1}
variable C2neg equal ${d2}
variable C3neg equal ${d3}
variable C4neg equal ${d4}
variable C5neg equal ${d5}
variable C6neg equal ${d6}

# Reset box and simulation parameters

clear
box tilt large
read_restart restart_FILENAME.equil
include ./input/angles_FILENAME.mod

# Positive deformation

variable delta equal ${up}*${len0}
variable deltaxy equal ${up}*xy
variable deltaxz equal ${up}*xz
variable deltayz equal ${up}*yz
if "${dir} == 1" then &
   "change_box all x delta 0 ${delta} xy delta ${deltaxy} xz delta ${deltaxz} remap units box"
if "${dir} == 2" then &
   "change_box all y delta 0 ${delta} yz delta ${deltayz} remap units box"
if "${dir} == 3" then &
   "change_box all z delta 0 ${delta} remap units box"
if "${dir} == 4" then &
   "change_box all yz delta ${delta} remap units box"
if "${dir} == 5" then &
   "change_box all xz delta ${delta} remap units box"
if "${dir} == 6" then &
   "change_box all xy delta ${delta} remap units box"

# Relax atoms positions

minimize ${etol} ${ftol} ${maxiter} ${maxeval}

# Obtain new stress tensor
 
variable tmp equal pe
variable e1 equal ${tmp}
variable tmp equal press
variable p1 equal ${tmp}
variable tmp equal pxx
variable pxx1 equal ${tmp}
variable tmp equal pyy
variable pyy1 equal ${tmp}
variable tmp equal pzz
variable pzz1 equal ${tmp}
variable tmp equal pxy
variable pxy1 equal ${tmp}
variable tmp equal pxz
variable pxz1 equal ${tmp}
variable tmp equal pyz
variable pyz1 equal ${tmp}

# Compute elastic constant from pressure tensor

variable C1pos equal ${d1}
variable C2pos equal ${d2}
variable C3pos equal ${d3}
variable C4pos equal ${d4}
variable C5pos equal ${d5}
variable C6pos equal ${d6}

# Combine positive and negative 

variable C1${dir} equal 0.5*(${C1neg}+${C1pos})
variable C2${dir} equal 0.5*(${C2neg}+${C2pos})
variable C3${dir} equal 0.5*(${C3neg}+${C3pos})
variable C4${dir} equal 0.5*(${C4neg}+${C4pos})
variable C5${dir} equal 0.5*(${C5neg}+${C5pos})
variable C6${dir} equal 0.5*(${C6neg}+${C6pos})

# Delete dir to make sure it is not reused

variable dir delete
EOF

sed -i "s/FILENAME/${filename}/g" ./input/in.${filename}
sed -i "s/FILENAME/${filename}/g" ./input/displace_${filename}.mod

awk '
  BEGIN{grab=0}
  /^Angle Coeffs/ {grab=1; next}
  /^[A-Za-z].*Coeffs/ {grab=0}
  grab {
    line=$0; sub(/#.*/,"",line); gsub(/^[ \t]+|[ \t]+$/,"",line)
    if(!line) next
    n=split(line,a)
    id=a[1]; style=a[2]
    if(!(style in seen)){ styles[++ns]=style; seen[style]=1 }
    sub("^[ \t]*"id"[ \t]+"style"[ \t]*","",line)
    lines[++nl]="angle_coeff " id " " style " " line
  }
  END{
    if(ns==1) printf "angle_style %s\n", styles[1]
    else { printf "angle_style hybrid"; for(i=1;i<=ns;i++) printf " %s", styles[i]; printf "\n" }
    for(i=1;i<=nl;i++) print lines[i]
  }
' ./dat/data.${filename} > ./input/angles_${filename}.mod

