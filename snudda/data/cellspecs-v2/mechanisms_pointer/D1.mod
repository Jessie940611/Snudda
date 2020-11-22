TITLE Mod file for component: Component(id=D1_reduced_cascade2_0 type=D1_reduced_cascade2)

COMMENT
    
    reduced speedy cascade from DA to phosphorylated target
    - second version 
    
    - original cascade implemented and exported to SBML by Anu Nair; nair at kth . se
        based on published cascade in Nair et al., 2016 with removed dependencies and
        addition of excitable target.
    
    - transformation from SBML to mod by Robert Lindroos; robert . lindroos at ki . se
        using NeuroML and a custom made python script that searches 
        the xml file and replaces the ID's of the substrates for the names.
        The script also shortens long names (e.g. reversable_reaction -> r_r)
        the name of the mechanism has alos been manually changed from D1_LTP_cascade... to
            D1_reduced_cascade2_0
            

    This NEURON file has been generated by org.neuroml.export (see https://github.com/NeuroML/org.neuroml.export)
         org.neuroml.export  v1.4.2
         org.neuroml.model   v1.4.2
         jLEMS               v0.9.7.3

ENDCOMMENT

NEURON {
    THREADSAFE
    POINT_PROCESS D1
    RANGE kGaolfGTPase: parameter
    RANGE kfPKA_2cAMP: parameter
    RANGE krPKA_2cAMP: parameter
    RANGE krPKAc_PKAr: parameter
    RANGE kfPKAc_PKAr: parameter
    RANGE kfPKA2cAMP_2cAMP: parameter
    RANGE krPKA2cAMP_2cAMP: parameter
    RANGE kactGolf: parameter
    RANGE kcatPDE4_cAMP: parameter
    RANGE kfPDE4_cAMP: parameter
    RANGE krPDE4_cAMP: parameter
    RANGE krPDE10_cAMP: parameter
    RANGE kcatPDE10c_cAMP: parameter
    RANGE kfPDE10_cAMP: parameter
    RANGE kfcAMP_PDE10: parameter
    RANGE krcAMP_PDE10: parameter
    RANGE kcatcAMP_PDE10: parameter
    RANGE kcatAC5GaolfGTP_ATP: parameter
    RANGE kicatAC5GaolfGTP_ATP: parameter
    RANGE kcatAC5_ATP: parameter
    RANGE kicatAC5_ATP: parameter
    RANGE kfAC5_ATP: parameter
    RANGE kGolfback: parameter
    RANGE kfAC5GaolfGTP_ATP: parameter
    RANGE kfD1R_Golf: parameter
    RANGE krD1R_Golf: parameter
    RANGE kfD1RDA_Golf: parameter
    RANGE krD1RDA_Golf: parameter
    RANGE krAC5X_ATP: parameter
    RANGE kfAC5XGaolfGTP: parameter
    RANGE krAC5XGaolfGTP: parameter
    RANGE krgso: parameter
    RANGE kfPDE10c_cAMP: parameter
    RANGE krPDE10c_cAMP: parameter
    RANGE kfD1R_DA: parameter
    RANGE kfD1RGolf_DA: parameter
    RANGE krD1R_DA: parameter
    RANGE krD1RGolf_DA: parameter
    RANGE kfPP1_Target1p                    : parameter
    RANGE krPP1_Target1p                    : parameter
    RANGE kfPKAc_Target1                    : parameter
    RANGE krPKAc_Target1                    : parameter
    RANGE kcatPP1_Target1p                  : parameter
    RANGE kcatPKAc_Target1                  : parameter
    RANGE tscale                            : parameter
    RANGE Spine: parameter
    RANGE init_GaolfGDP: parameter
    RANGE init_Gbgolf: parameter
    RANGE init_GaolfGTP: parameter
    RANGE init_D1RDAGolf: parameter
    RANGE init_Golf: parameter
    RANGE init_D1RGolf: parameter
    RANGE init_D1RDA: parameter
    RANGE init_D1R: parameter
    RANGE init_cAMP: parameter
    RANGE init_AC5: parameter
    RANGE init_AC5GaolfGTP: parameter
    RANGE init_PDE4: parameter
    RANGE init_PKA: parameter
    RANGE init_PKAcAMP2: parameter
    RANGE init_PKAcAMP4: parameter
    RANGE init_PKAreg: parameter
    RANGE init_PKAc: parameter
    RANGE init_PP1: parameter
    RANGE init_DA: parameter
    RANGE init_AMP: parameter
    RANGE init_PDE4_cAMP: parameter
    RANGE init_PDE10c: parameter
    RANGE init_PDE10: parameter
    RANGE init_PDE10_cAMP: parameter
    RANGE init_PDE10c_cAMP: parameter
    RANGE init_ATP: parameter
    RANGE init_AC5GaolfGTP_ATP: parameter
    RANGE init_AC5_ATP: parameter
    RANGE init_PP1_Target1p                 : parameter
    RANGE init_Target1p                     : parameter
    RANGE init_PKAc_Target1                 : parameter
    RANGE init_Target1                      : parameter
    RANGE r_r_1               : derived variable
    RANGE r_r_2               : derived variable
    RANGE r_r_3               : derived variable
    RANGE r_r_4               : derived variable
    RANGE r_r_5               : derived variable
    RANGE r_r_6               : derived variable
    RANGE r_r_7               : derived variable
    RANGE r_r_8               : derived variable
    RANGE r_r_9               : derived variable
    RANGE r_r_10              : derived variable
    RANGE r_r_11              : derived variable
    RANGE r_r_12              : derived variable
    RANGE r_r_13              : derived variable
    RANGE r_r_14              : derived variable
    RANGE r_r_15              : derived variable
    RANGE r_ir_1             : derived variable
    RANGE r_ir_2             : derived variable
    RANGE r_ir_3             : derived variable
    RANGE r_ir_4             : derived variable
    RANGE r_ir_5             : derived variable
    RANGE r_ir_6             : derived variable
    RANGE r_ir_7             : derived variable
    RANGE r_ir_8             : derived variable
    RANGE r_ir_9             : derived variable
    RANGE r_ir_10            : derived variable
    RANGE r_ir_11            : derived variable
    RANGE r_ir_12            : derived variable
    RANGE r_r_17              : derived variable
    RANGE r_r_16              : derived variable
    RANGE r_ir_14            : derived variable
    RANGE r_ir_15            : derived variable
    
}

UNITS {
    
    (nA) = (nanoamp)
    (uA) = (microamp)
    (mA) = (milliamp)
    (A) = (amp)
    (mV) = (millivolt)
    (mS) = (millisiemens)
    (uS) = (microsiemens)
    (molar) = (1/liter)
    (kHz) = (kilohertz)
    (mM) = (millimolar)
    (um) = (micrometer)
    (umol) = (micromole)
    (S) = (siemens)
    
}

PARAMETER {
    
    kGaolfGTPase = 30 
    kfPKA_2cAMP = 0.026 
    krPKA_2cAMP = 350 
    krPKAc_PKAr = 50 
    kfPKAc_PKAr = 0.03 
    kfPKA2cAMP_2cAMP = 0.0346 
    krPKA2cAMP_2cAMP = 50 
    kactGolf = 15 
    kcatPDE4_cAMP = 2.5 
    kfPDE4_cAMP = 0.03 
    krPDE4_cAMP = 1 
    krPDE10_cAMP = 1 
    kcatPDE10c_cAMP = 10 
    kfPDE10_cAMP = 1.0E-6 
    kfcAMP_PDE10 = 0.1 
    krcAMP_PDE10 = 2 
    kcatcAMP_PDE10 = 3 
    kcatAC5GaolfGTP_ATP = 50 
    kicatAC5GaolfGTP_ATP = 2.55 
    kcatAC5_ATP = 1 
    kicatAC5_ATP = 0.002 
    kfAC5_ATP = 1.0E-4 
    kGolfback = 100 
    kfAC5GaolfGTP_ATP = 0.00255 
    kfD1R_Golf = 0.06 
    krD1R_Golf = 250 
    kfD1RDA_Golf = 0.06 
    krD1RDA_Golf = 250 
    krAC5X_ATP = 1 
    kfAC5XGaolfGTP = 10 
    krAC5XGaolfGTP = 1 
    krgso = 1 
    kfPDE10c_cAMP = 0.1 
    krPDE10c_cAMP = 2 
    kfD1R_DA = 0.05 
    kfD1RGolf_DA = 0.05 
    krD1R_DA = 250 
    krD1RGolf_DA = 250 
    kfPP1_Target1p = 0.001 
    krPP1_Target1p = 10 
    kfPKAc_Target1 = 0.08 
    krPKAc_Target1 = 10 
    kcatPP1_Target1p = 5 
    kcatPKAc_Target1 = 10 
    tscale = 0.001 (kHz)
    Spine = 1.0E-15 
    init_GaolfGDP = 0.010083121 
    init_Gbgolf = 29.885124 
    init_GaolfGTP = 0.008913481 
    init_D1RDAGolf = 2.008902 
    init_Golf = 1453.0726 
    init_D1RGolf = 515.0334 
    init_D1RDA = 5.959225 
    init_D1R = 1476.9984 
    init_cAMP = 38.186016 
    init_AC5 = 2.6694465 
    init_AC5GaolfGTP = 0.118090406 
    init_PDE4 = 1506.8085 
    init_PKA = 1157.1414 
    init_PKAcAMP2 = 3.2824342 
    init_PKAcAMP4 = 0.08673742 
    init_PKAreg = 39.48949 
    init_PKAc = 3.6607807 
    init_PP1 = 2927.3425 
    init_DA = 20 
    init_AMP = 0 
    init_PDE4_cAMP = 493.19153 
    init_PDE10c = 0.5781013 
    init_PDE10 = 396.45627 
    init_PDE10_cAMP = 302.78168 
    init_PDE10c_cAMP = 0.18396154 
    init_ATP = 5000000 
    init_AC5GaolfGTP_ATP = 29.748037 
    init_AC5_ATP = 667.4644 
    init_PP1_Target1p = 73.65742 
    init_Target1p = 377.42807 
    init_PKAc_Target1 = 36.82871 
    init_Target1 = 2515.0857 
}

ASSIGNED {
    
    r_r_1                    : derived variable
    
    r_r_2                    : derived variable
    
    r_r_3                    : derived variable
    
    r_r_4                    : derived variable
    
    r_r_5                    : derived variable
    
    r_r_6                    : derived variable
    
    r_r_7                    : derived variable
    
    r_r_8                    : derived variable
    
    r_r_9                    : derived variable
    
    r_r_10                   : derived variable
    
    r_r_11                   : derived variable
    
    r_r_12                   : derived variable
    
    r_r_13                   : derived variable
    
    r_r_14                   : derived variable
    
    r_r_15                   : derived variable
    
    r_ir_1                  : derived variable
    
    r_ir_2                  : derived variable
    
    r_ir_3                  : derived variable
    
    r_ir_4                  : derived variable
    
    r_ir_5                  : derived variable
    
    r_ir_6                  : derived variable
    
    r_ir_7                  : derived variable
    
    r_ir_8                  : derived variable
    
    r_ir_9                  : derived variable
    
    r_ir_10                 : derived variable
    
    r_ir_11                 : derived variable
    
    r_ir_12                 : derived variable
    
    r_r_17                   : derived variable
    
    r_r_16                   : derived variable
    
    r_ir_14                 : derived variable
    
    r_ir_15                 : derived variable
    rate_GaolfGDP (/ms)
    rate_PKAreg (/ms)
    rate_AC5_ATP (/ms)
    rate_AC5GaolfGTP_ATP (/ms)
    rate_PKAcAMP4 (/ms)
    rate_AC5GaolfGTP (/ms)
    rate_PP1 (/ms)
    rate_Gbgolf (/ms)
    rate_PDE10 (/ms)
    rate_GaolfGTP (/ms)
    rate_PDE10_cAMP (/ms)
    rate_Target1p (/ms)
    rate_PDE10c (/ms)
    rate_cAMP (/ms)
    rate_AC5 (/ms)
    rate_PDE10c_cAMP (/ms)
    rate_D1RDAGolf (/ms)
    rate_D1RGolf (/ms)
    rate_PKAc_Target1 (/ms)
    rate_Target1 (/ms)
    rate_D1R (/ms)
    rate_D1RDA (/ms)
    rate_PP1_Target1p (/ms)
    rate_Golf (/ms)
    rate_PKA (/ms)
    rate_PKAc (/ms)
    rate_PDE4 (/ms)
    rate_PDE4_cAMP (/ms)
    rate_PKAcAMP2 (/ms)
    
}

STATE {
    GaolfGDP 
    Gbgolf 
    GaolfGTP 
    D1RDAGolf 
    Golf 
    D1RGolf 
    D1RDA 
    D1R 
    cAMP 
    AC5 
    AC5GaolfGTP 
    PDE4 
    PKA 
    PKAcAMP2 
    PKAcAMP4 
    PKAreg 
    PKAc 
    PP1 
    DA 
    AMP 
    PDE4_cAMP 
    PDE10c 
    PDE10 
    PDE10_cAMP 
    PDE10c_cAMP 
    ATP 
    AC5GaolfGTP_ATP 
    AC5_ATP 
    PP1_Target1p 
    Target1p 
    PKAc_Target1 
    Target1 
    
}

INITIAL {
    rates()
    rates() ? To ensure correct initialisation.
    
    GaolfGDP = init_GaolfGDP
    
    Gbgolf = init_Gbgolf
    
    GaolfGTP = init_GaolfGTP
    
    D1RDAGolf = init_D1RDAGolf
    
    Golf = init_Golf
    
    D1RGolf = init_D1RGolf
    
    D1RDA = init_D1RDA
    
    D1R = init_D1R
    
    cAMP = init_cAMP
    
    AC5 = init_AC5
    
    AC5GaolfGTP = init_AC5GaolfGTP
    
    PDE4 = init_PDE4
    
    PKA = init_PKA
    
    PKAcAMP2 = init_PKAcAMP2
    
    PKAcAMP4 = init_PKAcAMP4
    
    PKAreg = init_PKAreg
    
    PKAc = init_PKAc
    
    PP1 = init_PP1
    
    DA = init_DA
    
    AMP = init_AMP
    
    PDE4_cAMP = init_PDE4_cAMP
    
    PDE10c = init_PDE10c
    
    PDE10 = init_PDE10
    
    PDE10_cAMP = init_PDE10_cAMP
    
    PDE10c_cAMP = init_PDE10c_cAMP
    
    ATP = init_ATP
    
    AC5GaolfGTP_ATP = init_AC5GaolfGTP_ATP
    
    AC5_ATP = init_AC5_ATP
    
    PP1_Target1p = init_PP1_Target1p
    
    Target1p = init_Target1p
    
    PKAc_Target1 = init_PKAc_Target1
    
    Target1 = init_Target1
    
}

BREAKPOINT {
    
    SOLVE states METHOD cnexp
    
    
}

DERIVATIVE states {
    rates()
    GaolfGDP' = rate_GaolfGDP 
    PKAreg' = rate_PKAreg 
    AC5_ATP' = rate_AC5_ATP 
    AC5GaolfGTP_ATP' = rate_AC5GaolfGTP_ATP 
    PKAcAMP4' = rate_PKAcAMP4 
    AC5GaolfGTP' = rate_AC5GaolfGTP 
    PP1' = rate_PP1 
    Gbgolf' = rate_Gbgolf 
    PDE10' = rate_PDE10 
    GaolfGTP' = rate_GaolfGTP 
    PDE10_cAMP' = rate_PDE10_cAMP 
    Target1p' = rate_Target1p 
    PDE10c' = rate_PDE10c 
    cAMP' = rate_cAMP 
    AC5' = rate_AC5 
    PDE10c_cAMP' = rate_PDE10c_cAMP 
    D1RDAGolf' = rate_D1RDAGolf 
    D1RGolf' = rate_D1RGolf 
    PKAc_Target1' = rate_PKAc_Target1 
    Target1' = rate_Target1 
    D1R' = rate_D1R 
    D1RDA' = rate_D1RDA 
    PP1_Target1p' = rate_PP1_Target1p 
    Golf' = rate_Golf 
    PKA' = rate_PKA 
    PKAc' = rate_PKAc 
    PDE4' = rate_PDE4 
    PDE4_cAMP' = rate_PDE4_cAMP 
    PKAcAMP2' = rate_PKAcAMP2 
    
}

PROCEDURE rates() {
    
    r_r_1 = (  Spine   * (((  kfD1RGolf_DA   *    D1RGolf   ) *    DA   ) - (  krD1RGolf_DA   *    D1RDAGolf   ))) ? evaluable
    r_r_2 = (  Spine   * (((  kfD1R_DA   *    D1R   ) *    DA   ) - (  krD1R_DA   *    D1RDA   ))) ? evaluable
    r_r_3 = (  Spine   * (((  kfD1R_Golf   *    D1R   ) *    Golf   ) - (  krD1R_Golf   *    D1RGolf   ))) ? evaluable
    r_r_4 = (  Spine   * (((  kfD1RDA_Golf   *    Golf   ) *    D1RDA   ) - (  krD1RDA_Golf   *    D1RDAGolf   ))) ? evaluable
    r_r_5 = (  Spine   * (((  kfAC5XGaolfGTP   *    AC5   ) *    GaolfGTP   ) - (  krAC5XGaolfGTP   *    AC5GaolfGTP   ))) ? evaluable
    r_r_6 = (  Spine   * (((  kfAC5GaolfGTP_ATP   *    AC5GaolfGTP   ) *    ATP   ) - (  krAC5X_ATP   *    AC5GaolfGTP_ATP   ))) ? evaluable
    r_r_7 = (  Spine   * (((  kfAC5_ATP   *    AC5   ) *    ATP   ) - (  krAC5X_ATP   *    AC5_ATP   ))) ? evaluable
    r_r_8 = (  Spine   * (((  kfAC5XGaolfGTP   *    GaolfGTP   ) *    AC5_ATP   ) - (  krAC5XGaolfGTP   *    AC5GaolfGTP_ATP   ))) ? evaluable
    r_r_9 = (  Spine   * (((  kfPDE4_cAMP   *    cAMP   ) *    PDE4   ) - (  krPDE4_cAMP   *    PDE4_cAMP   ))) ? evaluable
    r_r_10 = (  Spine   * (((  kfPDE10_cAMP   *    PDE10   ) * (   cAMP    ^ 2.0)) - (  krPDE10_cAMP   *    PDE10c   ))) ? evaluable
    r_r_11 = (  Spine   * (((  kfcAMP_PDE10   *    cAMP   ) *    PDE10   ) - (  krcAMP_PDE10   *    PDE10_cAMP   ))) ? evaluable
    r_r_12 = (  Spine   * (((  kfPDE10c_cAMP   *    cAMP   ) *    PDE10c   ) - (  krPDE10c_cAMP   *    PDE10c_cAMP   ))) ? evaluable
    r_r_13 = (  Spine   * (((  kfPKA_2cAMP   *    cAMP   ) *    PKA   ) - (  krPKA_2cAMP   *    PKAcAMP2   ))) ? evaluable
    r_r_14 = (  Spine   * (((  kfPKA2cAMP_2cAMP   *    cAMP   ) *    PKAcAMP2   ) - (  krPKA2cAMP_2cAMP   *    PKAcAMP4   ))) ? evaluable
    r_r_15 = (  Spine   * ((  krPKAc_PKAr   *    PKAcAMP4   ) - ((  kfPKAc_PKAr   *    PKAc   ) *    PKAreg   ))) ? evaluable
    r_ir_1 = ((  Spine   *   kactGolf  ) *    D1RDAGolf   ) ? evaluable
    r_ir_2 = ((  Spine   *   kGaolfGTPase  ) *    GaolfGTP   ) ? evaluable
    r_ir_3 = (((  Spine   *   kGolfback  ) *    GaolfGDP   ) *    Gbgolf   ) ? evaluable
    r_ir_4 = ((  Spine   *   kcatAC5GaolfGTP_ATP  ) *    AC5GaolfGTP_ATP   ) ? evaluable
    r_ir_5 = (((  Spine   *   kicatAC5GaolfGTP_ATP  ) *    cAMP   ) *    AC5GaolfGTP   ) ? evaluable
    r_ir_6 = ((  Spine   *   kcatAC5_ATP  ) *    AC5_ATP   ) ? evaluable
    r_ir_7 = (((  Spine   *   kicatAC5_ATP  ) *    cAMP   ) *    AC5   ) ? evaluable
    r_ir_8 = ((  Spine   *   krgso  ) *    AC5GaolfGTP   ) ? evaluable
    r_ir_9 = ((  Spine   *   krgso  ) *    AC5GaolfGTP_ATP   ) ? evaluable
    r_ir_10 = ((  Spine   *   kcatPDE4_cAMP  ) *    PDE4_cAMP   ) ? evaluable
    r_ir_11 = ((  Spine   *   kcatcAMP_PDE10  ) *    PDE10_cAMP   ) ? evaluable
    r_ir_12 = ((  Spine   *   kcatPDE10c_cAMP  ) *    PDE10c_cAMP   ) ? evaluable
    r_r_17 = (  Spine   * (((  kfPP1_Target1p   *    PP1   ) *    Target1p   ) - (  krPP1_Target1p   *    PP1_Target1p   ))) ? evaluable
    r_r_16 = (  Spine   * (((  kfPKAc_Target1   *    Target1   ) *    PKAc   ) - (  krPKAc_Target1   *    PKAc_Target1   ))) ? evaluable
    r_ir_14 = ((  Spine   *   kcatPKAc_Target1  ) *    PKAc_Target1   ) ? evaluable
    r_ir_15 = ((  Spine   *   kcatPP1_Target1p  ) *    PP1_Target1p   ) ? evaluable
    rate_AC5GaolfGTP = tscale  * (  r_r_5   -  r_r_6  +  r_ir_4  -  r_ir_5  -   r_ir_8  ) /  Spine ? Note units of all quantities used here need to be consistent!
    rate_Gbgolf = tscale  * (  r_ir_1   -   r_ir_3  ) /  Spine ? Note units of all quantities used here need to be consistent!
    rate_PDE4_cAMP = tscale  * (  r_r_9   -   r_ir_10  ) /  Spine ? Note units of all quantities used here need to be consistent!
    rate_AC5GaolfGTP_ATP = tscale  * (  r_r_6   +  r_r_8  -  r_ir_4  +  r_ir_5  -   r_ir_9  ) /  Spine ? Note units of all quantities used here need to be consistent!
    rate_PP1 = tscale  * (-1*  r_r_17   +   r_ir_15  ) /  Spine ? Note units of all quantities used here need to be consistent!
    rate_PDE4 = tscale  * (-1*  r_r_9   +   r_ir_10  ) /  Spine ? Note units of all quantities used here need to be consistent!
    rate_PKAreg = tscale  * (  r_r_15  ) /  Spine ? Note units of all quantities used here need to be consistent!
    rate_GaolfGDP = tscale  * (  r_ir_2   -  r_ir_3  +  r_ir_8  +   r_ir_9  ) /  Spine ? Note units of all quantities used here need to be consistent!
    rate_AC5 = tscale  * (-1*  r_r_5   -  r_r_7  +  r_ir_6  -  r_ir_7  +   r_ir_8  ) /  Spine ? Note units of all quantities used here need to be consistent!
    rate_cAMP = tscale  * (-1*  r_r_9   -  r_r_10  * 2.0 -  r_r_11  -  r_r_12  -  r_r_13  -  r_r_14  +  r_ir_4  -  r_ir_5  +  r_ir_6  -   r_ir_7  ) /  Spine ? Note units of all quantities used here need to be consistent!
    rate_GaolfGTP = tscale  * (-1*  r_r_5   -  r_r_8  +  r_ir_1  -   r_ir_2  ) /  Spine ? Note units of all quantities used here need to be consistent!
    rate_PDE10_cAMP = tscale  * (  r_r_11   -   r_ir_11  ) /  Spine ? Note units of all quantities used here need to be consistent!
    rate_PKAcAMP4 = tscale  * (  r_r_14   -   r_r_15  ) /  Spine ? Note units of all quantities used here need to be consistent!
    rate_PDE10c = tscale  * (  r_r_10   -  r_r_12  +   r_ir_12  ) /  Spine ? Note units of all quantities used here need to be consistent!
    rate_PDE10c_cAMP = tscale  * (  r_r_12   -   r_ir_12  ) /  Spine ? Note units of all quantities used here need to be consistent!
    rate_PDE10 = tscale  * (-1*  r_r_10   -  r_r_11  +   r_ir_11  ) /  Spine ? Note units of all quantities used here need to be consistent!
    rate_Target1 = tscale  * (-1*  r_r_16   +   r_ir_15  ) /  Spine ? Note units of all quantities used here need to be consistent!
    rate_Target1p = tscale  * (-1*  r_r_17   +   r_ir_14  ) /  Spine ? Note units of all quantities used here need to be consistent!
    rate_D1RDA = tscale  * (  r_r_2   -  r_r_4  +   r_ir_1  ) /  Spine ? Note units of all quantities used here need to be consistent!
    rate_D1R = tscale  * (-1*  r_r_2   -   r_r_3  ) /  Spine ? Note units of all quantities used here need to be consistent!
    rate_Golf = tscale  * (-1*  r_r_3   -  r_r_4  +   r_ir_3  ) /  Spine ? Note units of all quantities used here need to be consistent!
    rate_PKA = tscale  * (-1*  r_r_13  ) /  Spine ? Note units of all quantities used here need to be consistent!
    rate_PKAc_Target1 = tscale  * (  r_r_16   -   r_ir_14  ) /  Spine ? Note units of all quantities used here need to be consistent!
    rate_PKAc = tscale  * (  r_r_15   -  r_r_16  +   r_ir_14  ) /  Spine ? Note units of all quantities used here need to be consistent!
    rate_PP1_Target1p = tscale  * (  r_r_17   -   r_ir_15  ) /  Spine ? Note units of all quantities used here need to be consistent!
    rate_PKAcAMP2 = tscale  * (  r_r_13   -   r_r_14  ) /  Spine ? Note units of all quantities used here need to be consistent!
    rate_D1RDAGolf = tscale  * (  r_r_1   +  r_r_4  -   r_ir_1  ) /  Spine ? Note units of all quantities used here need to be consistent!
    rate_D1RGolf = tscale  * (-1*  r_r_1   +   r_r_3  ) /  Spine ? Note units of all quantities used here need to be consistent!
    rate_AC5_ATP = tscale  * (  r_r_7   -  r_r_8  -  r_ir_6  +  r_ir_7  +   r_ir_9  ) /  Spine ? Note units of all quantities used here need to be consistent!
    
     
    
}
