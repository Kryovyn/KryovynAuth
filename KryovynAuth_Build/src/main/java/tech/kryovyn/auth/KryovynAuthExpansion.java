package tech.kryovyn.auth;
import me.clip.placeholderapi.expansion.PlaceholderExpansion;
import org.bukkit.OfflinePlayer; import org.bukkit.entity.Player;
import org.jetbrains.annotations.NotNull;
public class KryovynAuthExpansion extends PlaceholderExpansion {
    private final KryovynAuth plugin;
    public KryovynAuthExpansion(KryovynAuth p){this.plugin=p;}
    @Override public @NotNull String getIdentifier(){return "kryovyn";}
    @Override public @NotNull String getAuthor(){return "Kryovyn Studio";}
    @Override public @NotNull String getVersion(){return "1.0.0";}
    @Override public boolean persist(){return true;}
    @Override public String onRequest(OfflinePlayer pl,@NotNull String par){
        if(pl==null||!pl.isOnline())return ""; Player p=pl.getPlayer(); if(p==null)return "";
        SessionManager sm=plugin.sessions(); SessionManager.Session s=sm.get(p.getUniqueId());
        SessionManager.CachedInfo ci=sm.getCache(p.getUniqueId());
        switch(par.toLowerCase()){
            case "authorized": return sm.isAuthorized(p)?"yes":"no";
            case "in_limbo": return sm.isInLimbo(p)?"yes":"no";
            case "linked_tg": return ci.tg?"yes":"no";
            case "linked_ds": return ci.ds?"yes":"no";
            case "links_count": return String.valueOf(ci.count);
            case "tfa_status": return ci.tfaEnabled?"yes":"no";
            case "trust_days": return String.valueOf(Settings.TRUST_DAYS);
        }
        return null;
    }
}
