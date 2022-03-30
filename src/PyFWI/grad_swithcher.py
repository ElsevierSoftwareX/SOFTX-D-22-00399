import PyFWI.rock_physics as rp
import numpy as np

class PcsParameterization:
    def __init__(self, rp_model='gassmann'):
        if rp_model == 'gassmann':
            self.grad_dv2pcs = grad_dv2pcs_gassmann
            self.pcs2dv = rp.pcs2dv_gassmann
            
        elif rp_model == 'han':
            self.grad_dv2pcs = grad_dv2pcs_han
            self.pcs2dv = rp.pcs2dv_han
        
        elif rp_model == 'vrh':
            self.grad_dv2pcs = grad_dv2pcs_vrh
            self.pcs2dv = rp.pcs2dv_vrh
            

def grad_dv2pcs_vrh(gdv, rock_properties, pcs_model):
    dv_model = rp.pcs2dv_gassmann(pcs_model, rock_properties)
    
    vp = dv_model['vp']
    vs = dv_model['vs']
    rho = dv_model['rho']
    
    phi = pcs_model['phi']
    cc = pcs_model['cc']
    sw = pcs_model['sw']
    
    k_q = rock_properties['k_q']
    k_c = rock_properties['k_c']
    k_w = rock_properties['k_w']
    k_h = rock_properties['k_h']
    
    mu_q = rock_properties['mu_q']
    mu_c = rock_properties['mu_c']
    
    rho_q = rock_properties['rho_q']
    rho_c = rock_properties['rho_c']
    rho_w = rock_properties['rho_w']
    rho_h = rock_properties['rho_h']
    
    rho_s = rp.weighted_average(rho_c, rho_q, cc)
    
    rho_f = rp.weighted_average(rho_w, rho_h, sw)
    
    kr = 1 / ((1 - phi) * (cc / k_c + (1 - cc)/k_q) + phi * (sw/k_w + (1-sw)/k_h))         


    gk, gmu, grho_kmr = grad_dv2kmr(gdv, vp, vs, rho)
    
    gk_phi, gmu_phi, grho_phi = grad_kmr2phi_vrh(kr, k_c, k_q, k_w, k_h, mu_c, mu_q, cc, sw, rho_s, rho_f)
    g_phi = gk * gk_phi + gmu * gmu_phi + grho_kmr * grho_phi
    
    gk_c, gmu_c, grho_c = grad_kmr2cc_vrh(kr, phi, k_c, mu_c, rho_c, k_q, mu_q, rho_q)
    g_cc = gk * gk_c + gmu * gmu_c + grho_kmr * grho_c
    
    gk_sw, gmu_sw, grho_sw = grad_kmr2sw_vrh(kr, phi, k_w, k_h, rho_w, rho_h)
    g_sw = gk * gk_sw + gmu * gmu_sw + grho_kmr * grho_sw
      
    grad= {
        'phi': g_phi,
        'cc': g_cc,
        'sw': g_sw
    }
    return grad


def grad_kmr2sw_vrh(kr, phi, kw, kh, rhow, rhoh):
    
    gkv_sw = phi * (kw - kh)
    gkr_sw = phi * kr**2 * (1/kh - 1/kw)
    gk_sw = 0.5 * (gkv_sw + gkr_sw)
    
    gmu_sw = np.zeros(gk_sw.shape)    
    
    grho_sw = phi * (rhow - rhoh)
    return gk_sw, gmu_sw, grho_sw


def grad_kmr2cc_vrh(kr, phi, kc, muc, rhoc, kq, muq, rhoq):
    
    gkv_c = (1 - phi) * (kc - kq)
    gkr_c = (1 - phi) * kr**2 * (1/kq - 1/kc)
    gk_c = 0.5 * (gkv_c + gkr_c)
    
    gmuv_c = (1 - phi) * (muc - muq)
    gmur_c = 0
    gmu_c = 0.5 * (gmuv_c + gmur_c)

    grho_c = (1 - phi) * (rhoc - rhoq)
    return gk_c, gmu_c, grho_c


def grad_kmr2phi_vrh(kr, kc, kq, kw, kh, muc, muq, cc, sw, rhos, rhof):
    # voigt
    gkv_phi = - kc * cc - kq * (1 - cc) + kw * sw + kh * (1 - sw)
    #Reuss
    gkr_phi = kr**2 * (cc/kc + (1 - cc)/kq - sw/kw - (1-sw)/kh)
    gk_phi = 0.5 * (gkv_phi + gkr_phi)
    
    gmuv_phi = - muc * cc - muq * (1 - cc)
    gmur_phi = 0
    gmu_phi = 0.5 * (gmuv_phi + gmur_phi)
    
    grho_phi = rhof - rhos
    
    return gk_phi, gmu_phi, grho_phi

#%% Gassmann 
def grad_dv2pcs_gassmann(gdv, rock_properties, pcs_model):
    dv_model = rp.pcs2dv_gassmann(pcs_model, rock_properties)
    
    vp = dv_model['vp']
    vs = dv_model['vs']
    rho = dv_model['rho']
    
    phi = pcs_model['phi']
    cc = pcs_model['cc']
    sw = pcs_model['sw']
    
    k_q = rock_properties['k_q']
    k_c = rock_properties['k_c']
    k_w = rock_properties['k_w']
    k_h = rock_properties['k_h']
    
    mu_q = rock_properties['mu_q']
    mu_c = rock_properties['mu_c']
    
    rho_q = rock_properties['rho_q']
    rho_c = rock_properties['rho_c']
    rho_w = rock_properties['rho_w']
    rho_h = rock_properties['rho_h']
    cs = rock_properties['cs']
    
    k_s = rp.weighted_average(k_c, k_q, cc)
    mu_s = rp.weighted_average(mu_c, mu_q, cc)
    rho_s = rp.weighted_average(rho_c, rho_q, cc)
    
    rho_f = rp.weighted_average(rho_w, rho_h, sw)
    k_f = rp.weighted_average(k_w, k_h, sw)
    
    gk, gmu, grho_kmr = grad_dv2kmr(gdv, vp, vs, rho)
    
    gk_phi, gmu_phi, grho_phi = grad_kmr2phi_gassmann(phi, k_s, mu_s, rho_s, k_f, rho_f, cs)
    g_phi = gk * gk_phi + gmu * gmu_phi + grho_kmr * grho_phi
    
    gk_c, gmu_c, grho_c = grad_kmr2cc_gassmann(phi, cc, k_c, mu_c, rho_c, k_q, mu_q, rho_q, k_f, cs)
    g_cc = gk * gk_c + gmu * gmu_c + grho_kmr * grho_c
    
    gk_sw, gmu_sw, grho_sw = grad_kmr2sw_gassmann(phi, cc, k_c, k_w, k_h, mu_c, rho_w, k_q, mu_q, rho_h, k_f, cs)
    g_sw = gk * gk_sw + gmu * gmu_sw + grho_kmr * grho_sw
      
    grad= {
        'phi': g_phi,#/1000,
        'cc': g_cc,#/1000,
        'sw': g_sw,#/1000
    }
    return grad


def grad_kmr2sw_gassmann(phi, cc, kc, kw, kh, muc, rhow, kq, muq, rhoh, kf, cs):
    ks = rp.weighted_average(kc, kq, cc)
    mus = rp.weighted_average(muc, muq, cc)
    
    gkf_sw = kw - kh
    
    gmud_sw = 0
        
    kd, mud = rp.drained_moduli(phi, ks, mus, cs) 
    delta = rp.delta_biot_gassmann(phi, kf, ks, kd)
    
    gdelta_sw = gkf_sw * delta /kf
    
    phi_p = 1 + phi 
    phi_delta= phi * (1 + delta)
    
    num = 1 - (phi_p * kd / ks)
    gk_sw = num * gkf_sw /phi_delta - \
        (phi * kd + kf * num) * phi * gdelta_sw/ (phi_delta ** 2)
    
    gmu_sw = gmud_sw
    
    grho_sw = phi * (rhow - rhoh)
    return gk_sw, gmu_sw, grho_sw


def grad_kmr2cc_gassmann(phi, cc, kc, muc, rhoc, kq, muq, rhoq, kf, cs):
    ks = rp.weighted_average(kc, kq, cc)
    mus = rp.weighted_average(muc, muq, cc)
    
    gks_c = kc - kq
    gmus_c = muc - muq
    
    gkd_c = gks_c * (1 - phi) / (1 + cs * phi)
    gmud_c = gmus_c * (1 - phi) / (1 + cs * phi * 3 / 2)
    
    kfks2 = kf / ks**2
    
    gdelta_c = ((phi - 1) * kfks2/phi) * (1 - 1/(1 + cs * phi)) * gks_c
    
    kd, mud = rp.drained_moduli(phi, ks, mus, cs) 
    delta = rp.delta_biot_gassmann(phi, kf, ks, kd)
    
    kfks = kf / ks
    phi_p = 1 + phi 
    phi_delta= phi * (1 + delta)
    
    
    gk_c = (phi * gkd_c + kfks2 * phi_p * (gks_c * kd - gkd_c * ks))/phi_delta - \
        (phi * kd + kf - kfks * phi_p * kd) * (phi * gdelta_c)/ (phi_delta ** 2)
    
    gmu_c = gmud_c
    
    grho_c = (1 - phi) * (rhoc - rhoq)
    return gk_c, gmu_c, grho_c


def grad_kmr2phi_gassmann(phi, ks, mus, rhos, kf, rhof, cs):
    gkd_phi = -ks * ((1 + cs) /(1 + cs * phi) ** 2)
    gmud_phi = -mus * ((1 + cs * 3/2) /(1 + cs * phi * 3/2) ** 2)
    
    gdelta_phi = - (kf /(ks * phi**2)) * (1 - (1/(1 + cs * phi))) + ((kf * (1 - phi))/(ks * phi)) * (cs / (1 + cs * phi)**2)
    
    kd, mud = rp.drained_moduli(phi, ks, mus, cs) 
    delta = rp.delta_biot_gassmann(phi, kf, ks, kd)
    
    kfks = kf / ks
    phi_p = 1 + phi 
    phi_delta= phi * (1 + delta)
    
    
    gk_phi = (kd + phi * gkd_phi - kfks * (kd + phi_p * gkd_phi))/phi_delta - \
        (phi * kd + kf - kfks * phi_p * kd) * (1 + delta + phi * gdelta_phi)/ (phi_delta ** 2)
    
    gmu_phi = gmud_phi
    
    grho_phi = rhof - rhos
    return gk_phi, gmu_phi, grho_phi

    
def grad_dv2kmr(gdv, vp, vs, rho):
    gvp = gdv['vp']
    gvs = gdv['vs']
    grho = gdv['rho']
    
    gvp_k = 1 / (2 * rho * vp)
    gvs_k = 0
    grho_k = 0
    gk = gvp * gvp_k + gvs * gvs_k + grho * grho_k
    
    gvp_mu = 2 / (3 * rho * vp)
    gvs_mu = 1 / (2 * rho * vs)  
    grho_mu = 0
    gmu = gvp * gvp_mu + gvs * gvs_mu + grho * grho_mu
    
    gvp_rho = - vp / (2 * rho)
    gvs_rho = - vs / (2 * rho)
    grho_rho = 1
    grho_kmr = gvp * gvp_rho + gvs * gvs_rho + grho * grho_rho
    
    return gk, gmu, grho_kmr


def grad_dv2pcs_han(gdv, rock_properties, pcs_model):

    gvp = gdv['vp']
    gvs = gdv['vs']
    grho_dv = gdv['rho']
    
    phi = pcs_model['phi']
    cc = pcs_model['cc']
    sw = pcs_model['sw']
    
    rho_q = rock_properties['rho_q']
    rho_c = rock_properties['rho_c']
    rho_w = rock_properties['rho_w']
    rho_h = rock_properties['rho_h']
    
    rho_s = rp.weighted_average(rho_c, rho_q, cc)
    rho_f = rp.weighted_average(rho_w, rho_h, sw)
        
    gvp_phi, gvs_phi, grho_phi = grad_dv2phi_han(rho_f, rho_s, a2=6.9, b2=4.7)
    g_phi = gvp * gvp_phi + gvs * gvs_phi + grho_dv * grho_phi
    
    gvp_c, gvs_c, grho_c = grad_dv2cc_han(phi, rho_c, rho_q, a3=2.2, b3=1.8)
    g_cc = gvp * gvp_c + gvs * gvs_c + grho_dv * grho_c
    
    gvp_sw, gvs_sw, grho_sw = grad_dv2sw_han(phi, rho_w, rho_h)
    g_sw = gvp * gvp_sw + gvs * gvs_sw + grho_dv * grho_sw
      
    grad= {
        'phi': g_phi,
        'cc': g_cc,
        'sw': g_sw,
    }
    return grad


def grad_dv2phi_han(rhof, rhos, a2=6.9, b2=4.7):
    
    gvp_phi = - a2 
    gvs_phi = - b2
    grho_phi = rhof - rhos
    
    return gvp_phi, gvs_phi, grho_phi


def grad_dv2cc_han(phi, rho_c, rho_q, a3=2.2, b3=1.8):
    
    gvp_cc = - a3 
    gvs_cc = - b3
    grho_cc = (1 - phi) * (rho_c - rho_q)
    
    return gvp_cc, gvs_cc, grho_cc


def grad_dv2sw_han(phi, rho_w, rho_h):
    
    gvp_sw = 0 
    gvs_sw = 0
    grho_sw = phi * (rho_w - rho_h)
    
    return gvp_sw, gvs_sw, grho_sw


def grad_lmd_to_vd(glam, gmu, grho, lam, mu, rho):
    """
    grad_lmr_to_vd switch the gradient.

    This function witch the gradient from (lambda, mu, rho)
    to (vp, vs, rho).

    Args:
        glam (ndarray): Gradient w.r.t. lambda
        gmu (ndarray): Gradient w.r.t. mu
        grho (ndarray): Gradient w.r.t. density
        lam (ndarray): Gradient w.r.t. lambda
        mu (ndarray): Gradient w.r.t. mu
        rho (ndarray): Gradient w.r.t. density
    
    Refrences:
         1. Hu et al, 2021, Direct updating of rock-physics properties using elastice full-waveform inversion
         2. Zhou and Lumely, 2021, Central-difference time-lapse 4D seismic full-waveform inversion
    """
    vp = np.sqrt((lam + 2 * mu) / rho)
    vs = np.sqrt(mu / rho)
    vs2 = vs ** 2
    vpvs = vp ** 2 - 2 * vs ** 2
    
    glam_vp = glam * 2 * vp * rho
    gmu_vp = gmu * 0
    grho_vp = grho * 0
    gvp = glam_vp + gmu_vp + grho_vp  

    glam_vs = glam * (-4 * rho * vs)
    gmu_vs = gmu * 2 * vs * rho
    grho_vs = grho * 0
    gvs = glam_vs + gmu_vs + grho_vs  # gvs

    glam_rho = glam * vpvs
    gmu_rho = gmu * vs2
    grho_rho = grho
    grho = glam_rho + gmu_rho + grho_rho

    return gvp.astype(np.float32), gvs.astype(np.float32), grho.astype(np.float32)


def grad_vd_to_lmd(gvp, gvs, grho, vp, vs, rho):
    """
    grad_vd_to_lmd [summary]

    [extended_summary]

    Args:
        glam ([type]): [description]
        gmu ([type]): [description]
        grho ([type]): [description]
        lam ([type]): [description]
        mu ([type]): [description]
        rho ([type]): [description]
    
    Refrences:
         1. Hu et al, 2021, Direct updating of rock-physics properties using elastice full-waveform inversion
         2. Zhou and Lumely, 2021, Central-difference time-lapse 4D seismic full-waveform inversion
    """
    
    gvp_lam = gvp / (2 * rho * vp)
    gvs_lam = gvs * 0
    grho_lam = grho * 0 
    glam = gvp_lam + gvs_lam + grho_lam  # glam

    gvp_mu = gvp / (rho * vp)
    gvs_mu = gvs / (2 * rho * vs)
    grho_mu = grho * 0
    gmu = gvp_mu + gvs_mu + grho_mu  # gmu

    gvp_rho = gvp * (- vp / 2 / rho)
    gvs_rho = gvs * (- vs / 2 / rho)
    grho_rho = grho
    grho = gvp_rho + gvs_rho + grho_rho


    return glam.astype(np.float32), gmu.astype(np.float32), grho.astype(np.float32) 

