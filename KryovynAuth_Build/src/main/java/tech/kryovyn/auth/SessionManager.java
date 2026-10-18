package tech.kryovyn.auth;
import com.google.gson.JsonArray; import com.google.gson.JsonElement; import com.google.gson.JsonObject;
import org.bukkit.Sound; import org.bukkit.entity.Player;
import org.bukkit.potion.PotionEffect; import org.bukkit.potion.PotionEffectType;
import java.util.Map; import java.util.UUID; import java.util.concurrent.ConcurrentHashMap;
public class SessionManager {
    public static class Session{public boolean authorized=false,inLimbo=false; public int sessionId=0; public String platform=""; public long expiresAt=0; public int attempts=0;}
    public static class CachedInfo{public boolean tg=false,ds=false,max=false,tfaEnabled=false; public int count=0;}
    private final KryovynAuth plugin; private final ApiClient api;
    private final Map<UUID,Session>sessions=new ConcurrentHashMap<>();
    private final Map<UUID,CachedInfo>cache=new ConcurrentHashMap<>();
    public SessionManager(KryovynAuth p,ApiClient a){this.plugin=p;this.api=a;}
    public Session get(UUID u){return sessions.get(u);}
    public CachedInfo getCache(UUID u){return cache.getOrDefault(u,new CachedInfo());}
    public boolean isAuthorized(Player p){
        if(p.hasPermission("kryovyn.auth.bypass"))return true;
        Session s=sessions.get(p.getUniqueId()); return s==null||s.authorized;
    }
    public boolean isInLimbo(Player p){Session s=sessions.get(p.getUniqueId());return s!=null&&s.inLimbo&&!s.authorized;}
    public void begin(Player p){
        UUID u=p.getUniqueId(); Session s=new Session(); sessions.put(u,s);
        JsonObject b=new JsonObject(); b.addProperty("uuid",u.toString()); b.addProperty("name",p.getName());
        b.addProperty("ip",p.getAddress()!=null?p.getAddress().getAddress().getHostAddress():"");
        b.addProperty("fingerprint",Utils.fingerprint(p)); b.addProperty("device_name",Utils.deviceName(p));
        b.addProperty("platform","select");
        api.callAsync("session_start",b).thenAccept(r->plugin.getServer().getScheduler().runTask(plugin,()->{
            if(!p.isOnline())return;
            if(r.has("error")&&(!r.has("ok")||!r.get("ok").getAsBoolean())){
                if(Settings.FAIL_MODE.equalsIgnoreCase("DROP"))p.kickPlayer(Utils.color(Settings.FAIL_KICK));
                else s.authorized=true; return;
            }
            String reason=r.has("reason")?r.get("reason").getAsString():"";
            if("not_linked".equals(reason)){s.authorized=true;p.sendMessage(Utils.color(Settings.PREFIX+"&7Хочешь защитить аккаунт? Введи &e/knlink tg"));return;}
            if(r.has("trusted")&&r.get("trusted").getAsBoolean()){s.authorized=true;return;}
            if(r.has("need_platform")&&r.get("need_platform").getAsBoolean()){
                JsonArray pls=r.getAsJsonArray("platforms"); CachedInfo ci=new CachedInfo();
                if(pls!=null)for(JsonElement el:pls){String pl=el.getAsJsonObject().get("platform").getAsString();
                    if("tg".equals(pl))ci.tg=true; else if("ds".equals(pl))ci.ds=true; else if("max".equals(pl))ci.max=true; ci.count++;}
                cache.put(u,ci);
                if(pls!=null&&pls.size()==1){sendCode(p,pls.get(0).getAsJsonObject().get("platform").getAsString());return;}
                applyLimbo(p); s.inLimbo=true;
                plugin.getServer().getScheduler().runTaskLater(plugin,()->AuthGui.openPlatform(p,ci),10L);
                return;
            }
            if(Settings.FAIL_MODE.equalsIgnoreCase("DROP"))p.kickPlayer(Utils.color(Settings.FAIL_KICK)); else s.authorized=true;
        }));
    }
    public void sendCode(Player p,String platform){
        Session s=sessions.get(p.getUniqueId()); if(s==null||s.authorized)return;
        JsonObject b=new JsonObject(); b.addProperty("uuid",p.getUniqueId().toString()); b.addProperty("name",p.getName());
        b.addProperty("ip",p.getAddress()!=null?p.getAddress().getAddress().getHostAddress():"");
        b.addProperty("fingerprint",Utils.fingerprint(p)); b.addProperty("device_name",Utils.deviceName(p));
        b.addProperty("platform",platform);
        api.callAsync("session_start",b).thenAccept(r->plugin.getServer().getScheduler().runTask(plugin,()->{
            if(!p.isOnline()||!r.has("ok")||!r.get("ok").getAsBoolean()){
                p.sendMessage(Utils.color(Settings.PREFIX+"&cОшибка отправки кода."));return;
            }
            s.sessionId=r.get("session").getAsInt(); s.platform=r.get("platform").getAsString();
            s.expiresAt=System.currentTimeMillis()+r.get("ttl").getAsLong()*1000L;
            p.closeInventory();
            try{p.playSound(p.getLocation(),Sound.BLOCK_NOTE_BLOCK_PLING,1f,1f);}catch(Throwable ignored){}
            p.sendMessage(Utils.color(Settings.MSG_CODE_SENT.replace("%prefix%",Settings.PREFIX).replace("%platform%",s.platform.toUpperCase()).replace("%example%","123456")));
            s.inLimbo=true; applyLimbo(p);
        }));
    }
    public void verifyCode(Player p,String code){
        Session s=sessions.get(p.getUniqueId()); if(s==null)return;
        if(s.authorized){p.sendMessage(Utils.color(Settings.MSG_ALREADY_AUTH.replace("%prefix%",Settings.PREFIX)));return;}
        if(s.sessionId==0){p.sendMessage(Utils.color(Settings.PREFIX+"&cСначала выбери платформу"));return;}
        if(System.currentTimeMillis()>s.expiresAt){p.kickPlayer(Utils.color(Settings.MSG_CODE_EXPIRED.replace("%prefix%",Settings.PREFIX)));return;}
        if(s.attempts>=5){p.kickPlayer("§cСлишком много попыток");return;}
        JsonObject b=new JsonObject(); b.addProperty("session",s.sessionId); b.addProperty("code",code.trim());
        b.addProperty("fingerprint",Utils.fingerprint(p)); b.addProperty("device_name",Utils.deviceName(p));
        b.addProperty("trust",false);
        api.callAsync("session_verify",b).thenAccept(r->plugin.getServer().getScheduler().runTask(plugin,()->{
            if(!p.isOnline())return;
            if(r.has("ok")&&r.get("ok").getAsBoolean()){
                s.authorized=true; s.inLimbo=false; removeLimbo(p);
                try{p.playSound(p.getLocation(),Sound.ENTITY_PLAYER_LEVELUP,1f,1f);}catch(Throwable ignored){}
                plugin.getServer().getScheduler().runTaskLater(plugin,()->AuthGui.openTrust(p),15L);
            } else {
                String reason=r.has("reason")?r.get("reason").getAsString():"error"; s.attempts++;
                if("expired".equals(reason))p.kickPlayer(Utils.color(Settings.MSG_CODE_EXPIRED.replace("%prefix%",Settings.PREFIX)));
                else p.sendMessage(Utils.color(Settings.MSG_CODE_WRONG.replace("%prefix%",Settings.PREFIX).replace("%left%",String.valueOf(5-s.attempts))));
            }
        }));
    }
    public void trustDevice(Player p,boolean yes){
        Session s=sessions.get(p.getUniqueId()); if(s==null||!s.authorized)return;
        p.closeInventory(); if(!yes){p.sendMessage(Utils.color(Settings.MSG_TRUST_NO.replace("%prefix%",Settings.PREFIX)));return;}
        JsonObject b=new JsonObject(); b.addProperty("uuid",p.getUniqueId().toString());
        b.addProperty("fingerprint",Utils.fingerprint(p)); b.addProperty("device_name",Utils.deviceName(p));
        b.addProperty("days",Settings.TRUST_DAYS);
        api.callAsync("device_trust",b).thenAccept(r->plugin.getServer().getScheduler().runTask(plugin,()->
            p.sendMessage(Utils.color(Settings.MSG_TRUST_OK.replace("%prefix%",Settings.PREFIX).replace("%days%",String.valueOf(Settings.TRUST_DAYS))))));
    }
    public void applyLimbo(Player p){
        if(Settings.LIMBO_BLINDNESS)p.addPotionEffect(new PotionEffect(PotionEffectType.BLINDNESS,Integer.MAX_VALUE,0,false,false));
        if(Settings.LIMBO_SLOWNESS)p.addPotionEffect(new PotionEffect(PotionEffectType.SLOW,Integer.MAX_VALUE,10,false,false));
    }
    public void removeLimbo(Player p){p.removePotionEffect(PotionEffectType.BLINDNESS);p.removePotionEffect(PotionEffectType.SLOW);}
    public void tick(){long now=System.currentTimeMillis();
        sessions.entrySet().removeIf(e->{Session s=e.getValue();
            if(s.inLimbo&&!s.authorized&&s.expiresAt>0&&now>s.expiresAt){
                Player p=plugin.getServer().getPlayer(e.getKey());
                if(p!=null&&p.isOnline())p.kickPlayer("§cСессия 2FA истекла");return true;}
            return false;});
    }
    public void remove(UUID u){sessions.remove(u);cache.remove(u);}
}
