import math

def calculate_q10_decay(temperatures, base_life, ph, moisture):
    """
    Simulates the physics engine underlying the Hybrid DeepBoost model.
    k(T) = k0 * Q10^((T - Tref)/10)
    """
    cumulative = 0.0
    for t in temperatures:
        # Base Q10 exponential accumulation
        cumulative = (cumulative * 1.3) + math.exp((t - 20) / 6.0)
        
    static_mod = (ph / 4.0) * (moisture / 0.8)
    shelf_life = (base_life * static_mod) - (cumulative / 4.0)
    
    return max(0.0, min(shelf_life, 40.0))
