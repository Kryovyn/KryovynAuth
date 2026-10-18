import os
F = {}
F["pom.xml"] = """<?xml version="1.0"?>
<project xmlns="http://maven.apache.org/POM/4.0.0">
<modelVersion>4.0.0</modelVersion>
<groupId>tech.kryovyn</groupId><artifactId>KryovynAuth</artifactId><version>1.0.0</version><packaging>jar</packaging>
<properties><maven.compiler.source>17</maven.compiler.source><maven.compiler.target>17</maven.compiler.target><project.build.sourceEncoding>UTF-8</project.build.sourceEncoding></properties>
<repositories>
<repository><id>papermc</id><url>https://repo.papermc.io/repository/maven-public/</url></repository>
<repository><id>placeholderapi</id><url>https://repo.extendedclip.com/content/repositories/placeholderapi/</url></repository>
</repositories>
<dependencies>
<dependency><groupId>io.papermc.paper</groupId><artifactId>paper-api</artifactId><version>1.20.4-R0.1-SNAPSHOT</version><scope>provided</scope></dependency>
<dependency><groupId>me.clip</groupId><artifactId>placeholderapi</artifactId><version>2.11.6</version><scope>provided</scope></dependency>
<dependency><groupId>com.google.code.gson</groupId><artifactId>gson</artifactId><version>2.11.0</version></dependency>
</dependencies>
<build><finalName>KryovynAuth</finalName><plugins>
<plugin><groupId>org.apache.maven.plugins</groupId><artifactId>maven-compiler-plugin</artifactId><version>3.11.0</version><configuration><source>17</source><target>17</target></configuration></plugin>
<plugin><groupId>org.apache.maven.plugins</groupId><artifactId>maven-shade-plugin</artifactId><version>3.5.3</version>
<executions><execution><phase>package</phase><goals><goal>shade</goal></goals>
<configuration><createDependencyReducedPom>false</createDependencyReducedPom>
<relocations><relocation><pattern>com.google.gson</pattern><shadedPattern>tech.kryovyn.auth.libs.gson</shadedPattern></relocation></relocations>
</configuration></execution></executions>
</plugin></plugins></build>
</project>
"""
F["src/main/resources/plugin.yml"] = """name: KryovynAuth
version: 1.0.0
main: tech.kryovyn.auth.KryovynAuth
api-version: '1.16'
author: Kryovyn Studio
description: Advanced 2FA + account linking
website: http://195.208.21.210
commands:
  knmenu: { description: Menu, usage: /knmenu, aliases: [knauth, kna] }
  knlogin: { description: Login, usage: /knlogin <code>, aliases: [login, 2fa, auth] }
  kncode: { description: Request code, usage: /kncode <tg|ds|max|all>, aliases: [code] }
  kntrust: { description: Trust device, usage: /kntrust <yes|no>, aliases: [trust] }
  knlink: { description: Link, usage: /knlink <tg|ds|max>, aliases: [link] }
  knprofile: { description: Profile, usage: /knprofile, aliases: [profile, mp] }
  kndevices: { description: Devices, usage: /kndevices, aliases: [devices] }
  knlogout: { description: Logout all, usage: /knlogout, aliases: [logout, logoutall] }
  kntg: { description: TG menu, usage: /kntg, aliases: [tg] }
  knds: { description: DS menu, usage: /knds, aliases: [ds] }
  knreload: { description: Reload, usage: /knreload }
permissions:
  kryovyn.auth.bypass: { description: No 2FA, default: op }
  kryovyn.auth.admin: { description: Admin commands, default: op }
"""
F["src/main/resources/config.yml"] = """api:
  url: "https://your-domain.com/api/auth.php"
  token: "YOUR_TOKEN_HERE"
  timeout: 8
fail-mode:
  behavior: ALLOW
  kick-message: |
    &c&lСЕРВИС АВТОРИЗАЦИИ НЕДОСТУПЕН
limbo:
  blindness: true
  slowness: true
  block-chat: true
  block-commands: true
  block-movement: true
  block-rotation: false
  block-interact: true
  block-damage: true
trust-days: 30
messages:
  prefix: "&8[&dKN&8] "
  code-sent: "%prefix%&fКод отправлен в &d%platform%&f. Введи: &e/knlogin %example%"
  code-wrong: "%prefix%&cНеверный код. Осталось: %left%"
  code-ok: "%prefix%&a&l✓ Вход подтверждён!"
  code-expired: "%prefix%&cСессия истекла. Перезайди."
  already-auth: "%prefix%&eТы уже авторизован."
  trust-ok: "%prefix%&a✅ Устройство сохранено на %days% дней."
  trust-no: "%prefix%&7Хорошо, не сохраняем."
  link-start: |
    %prefix%&7Привязка к &b%platform%&7:
    &f1. Открой: &b%bot_url%
    &f2. Отправь: &e%command%
  link-already: "%prefix%&eУже привязано к %platform%."
  devices-none: "%prefix%&7Нет доверенных устройств."
  logoutall-ok: "%prefix%&aВсе устройства сброшены."
  only-player: "%prefix%&cТолько для игроков."
"""
# ============ Settings.java ============
F["src/main/java/tech/kryovyn/auth/Settings.java"] = """package tech.kryovyn.auth;
import org.bukkit.configuration.file.FileConfiguration;
public final class Settings {
    private Settings() {}
    public static String API_URL = ""; public static String API_TOKEN = "";
    public static int API_TIMEOUT = 8;
    public static String FAIL_MODE = "ALLOW"; public static String FAIL_KICK = "";
    public static boolean LIMBO_BLINDNESS=true, LIMBO_SLOWNESS=true, LIMBO_BLOCK_CHAT=true,
        LIMBO_BLOCK_COMMANDS=true, LIMBO_BLOCK_MOVEMENT=true, LIMBO_BLOCK_ROTATION=false,
        LIMBO_BLOCK_INTERACT=true, LIMBO_BLOCK_DAMAGE=true;
    public static int TRUST_DAYS = 30;
    public static String PREFIX="&8[&dKN&8] ",
        MSG_CODE_SENT="", MSG_CODE_WRONG="", MSG_CODE_OK="", MSG_CODE_EXPIRED="",
        MSG_ALREADY_AUTH="", MSG_TRUST_OK="", MSG_TRUST_NO="", MSG_LINK_START="",
        MSG_LINK_ALREADY="", MSG_DEVICES_NONE="", MSG_LOGOUTALL_OK="", MSG_ONLY_PLAYER="";
    public static void load(FileConfiguration c) {
        API_URL=c.getString("api.url",API_URL); API_TOKEN=c.getString("api.token","");
        API_TIMEOUT=c.getInt("api.timeout",8);
        FAIL_MODE=c.getString("fail-mode.behavior","ALLOW");
        FAIL_KICK=c.getString("fail-mode.kick-message","");
        LIMBO_BLINDNESS=c.getBoolean("limbo.blindness",true);
        LIMBO_SLOWNESS=c.getBoolean("limbo.slowness",true);
        LIMBO_BLOCK_CHAT=c.getBoolean("limbo.block-chat",true);
        LIMBO_BLOCK_COMMANDS=c.getBoolean("limbo.block-commands",true);
        LIMBO_BLOCK_MOVEMENT=c.getBoolean("limbo.block-movement",true);
        LIMBO_BLOCK_ROTATION=c.getBoolean("limbo.block-rotation",false);
        LIMBO_BLOCK_INTERACT=c.getBoolean("limbo.block-interact",true);
        LIMBO_BLOCK_DAMAGE=c.getBoolean("limbo.block-damage",true);
        TRUST_DAYS=c.getInt("trust-days",30);
        PREFIX=c.getString("messages.prefix",PREFIX);
        MSG_CODE_SENT=c.getString("messages.code-sent",""); MSG_CODE_WRONG=c.getString("messages.code-wrong","");
        MSG_CODE_OK=c.getString("messages.code-ok",""); MSG_CODE_EXPIRED=c.getString("messages.code-expired","");
        MSG_ALREADY_AUTH=c.getString("messages.already-auth",""); MSG_TRUST_OK=c.getString("messages.trust-ok","");
        MSG_TRUST_NO=c.getString("messages.trust-no",""); MSG_LINK_START=c.getString("messages.link-start","");
        MSG_LINK_ALREADY=c.getString("messages.link-already","");
        MSG_DEVICES_NONE=c.getString("messages.devices-none","");
        MSG_LOGOUTALL_OK=c.getString("messages.logoutall-ok","");
        MSG_ONLY_PLAYER=c.getString("messages.only-player","");
    }
}
"""
# ============ Utils.java ============
F["src/main/java/tech/kryovyn/auth/Utils.java"] = """package tech.kryovyn.auth;
import org.bukkit.ChatColor; import org.bukkit.entity.Player;
import java.nio.charset.StandardCharsets; import java.security.MessageDigest;
public final class Utils {
    private Utils() {}
    public static String color(String s){return ChatColor.translateAlternateColorCodes('&',s==null?"":s);}
    public static String fingerprint(Player p){
        String brand; try{brand=p.getClientBrandName();if(brand==null)brand="vanilla";}catch(Throwable t){brand="unknown";}
        String raw=p.getUniqueId()+"|"+brand+"|"+getProto(p);
        try{MessageDigest md=MessageDigest.getInstance("SHA-256");byte[] h=md.digest(raw.getBytes(StandardCharsets.UTF_8));
            StringBuilder sb=new StringBuilder();for(byte b:h)sb.append(String.format("%02x",b));return sb.substring(0,16);
        }catch(Exception e){return Integer.toHexString(raw.hashCode());}
    }
    public static String deviceName(Player p){
        String ip=p.getAddress()!=null?p.getAddress().getAddress().getHostAddress():"?";
        String brand; try{brand=p.getClientBrandName();if(brand==null)brand="vanilla";}catch(Throwable t){brand="unknown";}
        return "IP "+ip+" · "+brand+" · proto "+getProto(p);
    }
    private static int getProto(Player p){try{return p.getProtocolVersion();}catch(Throwable t){return 0;}}
}
"""
# ============ ApiClient.java ============
F["src/main/java/tech/kryovyn/auth/ApiClient.java"] = """package tech.kryovyn.auth;
import com.google.gson.Gson; import com.google.gson.JsonObject;
import java.net.URI; import java.net.http.HttpClient; import java.net.http.HttpRequest;
import java.net.http.HttpResponse; import java.time.Duration; import java.util.concurrent.CompletableFuture;
import java.util.logging.Level;
public class ApiClient {
    private static final HttpClient HTTP = HttpClient.newBuilder().connectTimeout(Duration.ofSeconds(15)).build();
    private final Gson gson = new Gson();
    public JsonObject call(String action, JsonObject body) {
        String url = Settings.API_URL + "?action=" + action;
        try {
            HttpRequest req = HttpRequest.newBuilder().uri(URI.create(url))
                .timeout(Duration.ofSeconds(Settings.API_TIMEOUT))
                .header("Content-Type","application/json").header("X-Auth-Token",Settings.API_TOKEN)
                .POST(HttpRequest.BodyPublishers.ofString(gson.toJson(body))).build();
            HttpResponse<String> resp = HTTP.send(req, HttpResponse.BodyHandlers.ofString());
            JsonObject out = gson.fromJson(resp.body(), JsonObject.class);
            return out != null ? out : err("empty");
        } catch (Exception e) {
            KryovynAuth.get().getLogger().log(Level.WARNING,"API fail: "+action,e);
            return err(e.getMessage());
        }
    }
    public CompletableFuture<JsonObject> callAsync(String a, JsonObject b){return CompletableFuture.supplyAsync(()->call(a,b));}
    private JsonObject err(String m){JsonObject o=new JsonObject();o.addProperty("ok",false);o.addProperty("error",m==null?"unknown":m);return o;}
}
"""
# ============ KryovynAuth.java ============
F["src/main/java/tech/kryovyn/auth/KryovynAuth.java"] = """package tech.kryovyn.auth;
import org.bukkit.plugin.java.JavaPlugin;
public final class KryovynAuth extends JavaPlugin {
    private static KryovynAuth instance;
    private ApiClient api; private SessionManager sessions;
    public static KryovynAuth get(){return instance;}
    @Override public void onEnable(){
        instance=this; saveDefaultConfig(); Settings.load(getConfig());
        api=new ApiClient(); sessions=new SessionManager(this,api);
        getServer().getPluginManager().registerEvents(new PlayerListener(this,sessions),this);
        Commands cmd=new Commands(this,sessions);
        for(String c:new String[]{"knmenu","knlogin","kncode","kntrust","knlink","knprofile","kndevices","knlogout","kntg","knds","knreload"}){
            if(getCommand(c)!=null)getCommand(c).setExecutor(cmd); else getLogger().warning("no cmd: "+c);
        }
        if(getServer().getPluginManager().getPlugin("PlaceholderAPI")!=null){
            new KryovynAuthExpansion(this).register(); getLogger().info("PAPI registered");
        }
        getServer().getScheduler().runTaskTimer(this,sessions::tick,100L,100L);
        getLogger().info("KryovynAuth enabled");
    }
    public ApiClient api(){return api;} public SessionManager sessions(){return sessions;}
}
"""
# ============ KryovynAuthExpansion.java ============
F["src/main/java/tech/kryovyn/auth/KryovynAuthExpansion.java"] = """package tech.kryovyn.auth;
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
"""
# ============ SessionManager.java ============
F["src/main/java/tech/kryovyn/auth/SessionManager.java"] = """package tech.kryovyn.auth;
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
"""
# ============ AuthGui.java ============
F["src/main/java/tech/kryovyn/auth/AuthGui.java"] = """package tech.kryovyn.auth;
import org.bukkit.Bukkit; import org.bukkit.Material; import org.bukkit.entity.Player;
import org.bukkit.inventory.Inventory; import org.bukkit.inventory.ItemStack; import org.bukkit.inventory.meta.ItemMeta;
import java.util.ArrayList; import java.util.List;
public final class AuthGui {
    public static final String TITLE_MAIN=Utils.color("&8» &d&lKryovyn &8» &fAuth &8«");
    public static final String TITLE_PLATFORM=Utils.color("&8» &d&lPlatform &8«");
    public static final String TITLE_TRUST=Utils.color("&8» &d&lTrust? &8«");
    public static final String TITLE_CONFIRM_LOGOUT=Utils.color("&8» &d&lReset? &8«");
    private AuthGui(){}
    private static ItemStack item(Material m,String n,String...l){
        ItemStack i=new ItemStack(m); ItemMeta im=i.getItemMeta();
        if(im!=null){im.setDisplayName(Utils.color(n));
            if(l.length>0){List<String>ll=new ArrayList<>();for(String s:l)ll.add(Utils.color(s));im.setLore(ll);}
            i.setItemMeta(im);} return i;
    }
    private static void fill(Inventory inv){
        ItemStack f=item(Material.PURPLE_STAINED_GLASS_PANE,"&d");
        for(int i=0;i<inv.getSize();i++)inv.setItem(i,f);
    }
    public static void openMain(Player p){
        Inventory inv=Bukkit.createInventory(null,27,TITLE_MAIN); fill(inv);
        inv.setItem(4,item(Material.NETHER_STAR,"&d&lKryovyn Auth","&7Player: &d"+p.getName()));
        inv.setItem(10,item(Material.PAPER,"&d&lProfile","&7Click"));
        inv.setItem(12,item(Material.BOOK,"&d&lDevices","&7Click"));
        inv.setItem(14,item(Material.PAPER,"&b&lLink TG","&7Click"));
        inv.setItem(15,item(Material.PURPLE_DYE,"&5&lLink DS","&7Click"));
        inv.setItem(22,item(Material.BARRIER,"&c&lReset devices","&cClick"));
        p.openInventory(inv);
    }
    public static void openPlatform(Player p,SessionManager.CachedInfo ci){
        Inventory inv=Bukkit.createInventory(null,27,TITLE_PLATFORM); fill(inv);
        inv.setItem(4,item(Material.NETHER_STAR,"&d&lEnter game","&7Pick platform"));
        if(ci.tg)inv.setItem(11,item(Material.PAPER,"&b&lTelegram","&bClick"));
        if(ci.ds)inv.setItem(13,item(Material.PURPLE_DYE,"&5&lDiscord","&5Click"));
        if(ci.max)inv.setItem(15,item(Material.SLIME_BALL,"&a&lMAX","&aClick"));
        if(ci.count>=2)inv.setItem(22,item(Material.NETHER_STAR,"&6&lAll","&6Click"));
        p.openInventory(inv);
    }
    public static void openTrust(Player p){
        Inventory inv=Bukkit.createInventory(null,27,TITLE_TRUST); fill(inv);
        inv.setItem(4,item(Material.SHIELD,"&d&lSave device?","&7Duration: &d"+Settings.TRUST_DAYS+" days"));
        inv.setItem(11,item(Material.LIME_DYE,"&a&lSave","&aClick"));
        inv.setItem(15,item(Material.RED_DYE,"&c&lSkip","&cClick"));
        p.openInventory(inv);
    }
    public static void openConfirmLogout(Player p){
        Inventory inv=Bukkit.createInventory(null,27,TITLE_CONFIRM_LOGOUT); fill(inv);
        inv.setItem(4,item(Material.SHIELD,"&d&lWarning","&7Reset ALL devices"));
        inv.setItem(11,item(Material.LIME_DYE,"&c&lYes","&cClick"));
        inv.setItem(15,item(Material.RED_DYE,"&a&lCancel","&aClick"));
        p.openInventory(inv);
    }
}
"""
# ============ PlayerListener.java ============
F["src/main/java/tech/kryovyn/auth/PlayerListener.java"] = """package tech.kryovyn.auth;
import org.bukkit.entity.Player; import org.bukkit.event.*;
import org.bukkit.event.block.*; import org.bukkit.event.entity.*;
import org.bukkit.event.inventory.*; import org.bukkit.event.player.*;
public class PlayerListener implements Listener {
    private final KryovynAuth plugin; private final SessionManager sessions;
    public PlayerListener(KryovynAuth p,SessionManager s){this.plugin=p;this.sessions=s;}
    private boolean locked(Player p){return !sessions.isAuthorized(p);}
    @EventHandler public void onJoin(PlayerJoinEvent e){
        if(e.getPlayer().hasPermission("kryovyn.auth.bypass"))return; sessions.begin(e.getPlayer());
    }
    @EventHandler public void onQuit(PlayerQuitEvent e){sessions.remove(e.getPlayer().getUniqueId());}
    @EventHandler(priority=EventPriority.HIGHEST)
    public void onInvClick(InventoryClickEvent e){
        if(!(e.getWhoClicked() instanceof Player p))return;
        String t=e.getView().getTitle();
        if(t.equals(AuthGui.TITLE_MAIN)){e.setCancelled(true);int s=e.getRawSlot();p.closeInventory();
            if(s==10)p.performCommand("knprofile"); else if(s==12)p.performCommand("kndevices");
            else if(s==14)p.performCommand("knlink tg"); else if(s==15)p.performCommand("knlink ds");
            else if(s==22)AuthGui.openConfirmLogout(p); return;}
        if(t.equals(AuthGui.TITLE_PLATFORM)){e.setCancelled(true);int s=e.getRawSlot();
            String pl=null; if(s==11)pl="tg"; else if(s==13)pl="ds"; else if(s==15)pl="max"; else if(s==22)pl="all";
            if(pl!=null){p.closeInventory();sessions.sendCode(p,pl);} return;}
        if(t.equals(AuthGui.TITLE_TRUST)){e.setCancelled(true);int s=e.getRawSlot();
            if(s==11)sessions.trustDevice(p,true); else if(s==15)sessions.trustDevice(p,false); return;}
        if(t.equals(AuthGui.TITLE_CONFIRM_LOGOUT)){e.setCancelled(true);int s=e.getRawSlot();p.closeInventory();
            if(s==11)p.performCommand("knlogout"); else if(s==15)AuthGui.openMain(p); return;}
        if(Settings.LIMBO_BLOCK_INTERACT&&locked(p))e.setCancelled(true);
    }
    @EventHandler(priority=EventPriority.LOWEST)
    public void onMove(PlayerMoveEvent e){
        if(!Settings.LIMBO_BLOCK_MOVEMENT||!locked(e.getPlayer()))return;
        if(Settings.LIMBO_BLOCK_ROTATION)e.setTo(e.getFrom());
        else if(e.getFrom().getBlockX()!=e.getTo().getBlockX()||e.getFrom().getBlockY()!=e.getTo().getBlockY()
            ||e.getFrom().getBlockZ()!=e.getTo().getBlockZ())e.setTo(e.getFrom());
    }
    @EventHandler(priority=EventPriority.LOWEST)
    public void onChat(AsyncPlayerChatEvent e){
        if(!Settings.LIMBO_BLOCK_CHAT||!locked(e.getPlayer()))return;
        e.setCancelled(true); e.getPlayer().sendMessage(Utils.color("&cВведи: /knlogin <code>"));
    }
    @EventHandler(priority=EventPriority.LOWEST)
    public void onCommand(PlayerCommandPreprocessEvent e){
        if(!Settings.LIMBO_BLOCK_COMMANDS||!locked(e.getPlayer()))return;
        String c=e.getMessage().split(" ")[0].toLowerCase();
        for(String a:new String[]{"/knlogin","/login","/2fa","/auth","/kncode","/code","/kntrust","/trust",
            "/knlink","/link","/knprofile","/profile","/mp","/kndevices","/devices","/knlogout","/logout",
            "/logoutall","/knmenu","/knauth","/kna","/kntg","/tg","/knds","/ds","/help"})
            if(c.equals(a)||c.startsWith(a+" "))return;
        if(c.startsWith("/kryovyn:"))return;
        e.setCancelled(true); e.getPlayer().sendMessage(Utils.color("&cВведи: /knlogin <code>"));
    }
    @EventHandler public void onInteract(PlayerInteractEvent e){if(Settings.LIMBO_BLOCK_INTERACT&&locked(e.getPlayer()))e.setCancelled(true);}
    @EventHandler public void onBreak(BlockBreakEvent e){if(Settings.LIMBO_BLOCK_INTERACT&&locked(e.getPlayer()))e.setCancelled(true);}
    @EventHandler public void onPlace(BlockPlaceEvent e){if(Settings.LIMBO_BLOCK_INTERACT&&locked(e.getPlayer()))e.setCancelled(true);}
    @EventHandler public void onDrop(PlayerDropItemEvent e){if(locked(e.getPlayer()))e.setCancelled(true);}
    @EventHandler public void onPickup(EntityPickupItemEvent e){if(e.getEntity() instanceof Player&&locked((Player)e.getEntity()))e.setCancelled(true);}
    @EventHandler public void onInvOpen(InventoryOpenEvent e){
        if(!(e.getPlayer() instanceof Player))return; Player p=(Player)e.getPlayer();
        if(!locked(p))return;
        String t=e.getView().getTitle();
        if(t.equals(AuthGui.TITLE_MAIN)||t.equals(AuthGui.TITLE_PLATFORM)||t.equals(AuthGui.TITLE_TRUST)||t.equals(AuthGui.TITLE_CONFIRM_LOGOUT))return;
        e.setCancelled(true);
    }
    @EventHandler(priority=EventPriority.LOWEST)
    public void onDamage(EntityDamageEvent e){
        if(!Settings.LIMBO_BLOCK_DAMAGE)return;
        if(e.getEntity() instanceof Player&&locked((Player)e.getEntity()))e.setCancelled(true);
    }
}
"""
# ============ Commands.java ============
F["src/main/java/tech/kryovyn/auth/Commands.java"] = """package tech.kryovyn.auth;
import com.google.gson.*; import org.bukkit.command.*; import org.bukkit.entity.Player;
public class Commands implements CommandExecutor {
    private final KryovynAuth plugin; private final SessionManager sessions;
    public Commands(KryovynAuth p,SessionManager s){this.plugin=p;this.sessions=s;}
    @Override public boolean onCommand(CommandSender s,Command c,String l,String[] a){
        if(!(s instanceof Player)){s.sendMessage(Utils.color(Settings.MSG_ONLY_PLAYER));return true;}
        Player p=(Player)s; String n=c.getName().toLowerCase();
        if(n.equals("knmenu")){AuthGui.openMain(p);return true;}
        if(n.equals("knlogin")){if(a.length!=1){p.sendMessage(Utils.color("&e/knlogin <code>"));return true;} sessions.verifyCode(p,a[0]); return true;}
        if(n.equals("kncode")){if(a.length!=1){p.sendMessage(Utils.color("&e/kncode <tg|ds|max|all>"));return true;} sessions.sendCode(p,a[0].toLowerCase()); return true;}
        if(n.equals("kntrust")){if(a.length!=1){p.sendMessage(Utils.color("&e/kntrust <yes|no>"));return true;} sessions.trustDevice(p,a[0].equalsIgnoreCase("yes")); return true;}
        if(n.equals("knlink")){if(a.length!=1){p.sendMessage(Utils.color("&e/knlink <tg|ds|max>"));return true;} return link(p,a[0]);}
        if(n.equals("kntg"))return link(p,"tg");
        if(n.equals("knds"))return link(p,"ds");
        if(n.equals("knprofile"))return profile(p);
        if(n.equals("kndevices"))return devices(p);
        if(n.equals("knlogout"))return logout(p);
        if(n.equals("knreload")){if(!p.hasPermission("kryovyn.auth.admin")){p.sendMessage(Utils.color("&cНет прав"));return true;} plugin.reloadConfig();Settings.load(plugin.getConfig());p.sendMessage(Utils.color("&a✅ Reloaded")); return true;}
        return true;
    }
    private boolean link(Player p,String platform){
        platform=platform.toLowerCase();
        if(!platform.equals("tg")&&!platform.equals("max")&&!platform.equals("ds")){p.sendMessage(Utils.color("&cДоступно: tg,ds,max"));return true;}
        JsonObject b=new JsonObject(); b.addProperty("uuid",p.getUniqueId().toString()); b.addProperty("name",p.getName()); b.addProperty("platform",platform);
        final String pf=platform;
        plugin.api().callAsync("link_start",b).thenAccept(r->plugin.getServer().getScheduler().runTask(plugin,()->{
            if(!p.isOnline())return;
            if(!r.has("ok")||!r.get("ok").getAsBoolean()){
                String reason=r.has("reason")?r.get("reason").getAsString():"?";
                if("already_linked".equals(reason))p.sendMessage(Utils.color(Settings.MSG_LINK_ALREADY.replace("%prefix%",Settings.PREFIX).replace("%platform%",pf.toUpperCase())));
                else p.sendMessage(Utils.color("&cОшибка: "+reason));
                return;
            }
            String m=Settings.MSG_LINK_START.replace("%prefix%",Settings.PREFIX).replace("%platform%",pf.toUpperCase())
                .replace("%bot_url%",r.get("bot_url").getAsString()).replace("%command%",r.get("command").getAsString());
            for(String line:m.split("\\n"))p.sendMessage(Utils.color(line));
        }));
        return true;
    }
    private boolean profile(Player p){
        JsonObject b=new JsonObject(); b.addProperty("uuid",p.getUniqueId().toString());
        plugin.api().callAsync("profile_by_uuid",b).thenAccept(r->plugin.getServer().getScheduler().runTask(plugin,()->{
            if(!p.isOnline()||!r.has("ok")||!r.get("ok").getAsBoolean()){p.sendMessage("§cОшибка");return;}
            JsonObject acc=r.getAsJsonObject("account");
            p.sendMessage(Utils.color(Settings.PREFIX+"&fНик: &b"+acc.get("mc_name").getAsString()));
            p.sendMessage(Utils.color("&8[&dKN&8] &72FA: "+(acc.get("tfa_enabled").getAsBoolean()?"&aвкл":"&cвыкл")));
            p.sendMessage(Utils.color("&8[&dKN&8] &7Устройств: &f"+acc.get("device_count").getAsInt()));
            p.sendMessage(Utils.color("&8[&dKN&8] &7Сессий: &f"+acc.get("active_sessions").getAsInt()));
        }));
        return true;
    }
    private boolean devices(Player p){
        JsonObject b=new JsonObject(); b.addProperty("uuid",p.getUniqueId().toString());
        plugin.api().callAsync("devices_by_uuid",b).thenAccept(r->plugin.getServer().getScheduler().runTask(plugin,()->{
            if(!p.isOnline()||!r.has("ok")||!r.get("ok").getAsBoolean()){p.sendMessage("§cОшибка");return;}
            JsonArray list=r.getAsJsonArray("devices");
            if(list==null||list.size()==0){p.sendMessage(Utils.color(Settings.MSG_DEVICES_NONE.replace("%prefix%",Settings.PREFIX)));return;}
            p.sendMessage(Utils.color("&fУстройства:"));
            for(JsonElement el:list){JsonObject d=el.getAsJsonObject();
                p.sendMessage(Utils.color(" &7- &f#"+d.get("id").getAsInt()+" "+d.get("name").getAsString()));
            }
        }));
        return true;
    }
    private boolean logout(Player p){
        JsonObject b=new JsonObject(); b.addProperty("uuid",p.getUniqueId().toString());
        plugin.api().callAsync("devices_revoke_all",b).thenAccept(r->plugin.getServer().getScheduler().runTask(plugin,()->
            p.sendMessage(Utils.color(Settings.MSG_LOGOUTALL_OK.replace("%prefix%",Settings.PREFIX)))));
        return true;
    }
}
"""
# Создание
for path, content in F.items():
    d = os.path.dirname(path)
    if d: os.makedirs(d, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print("Created:", path)
print("\nDONE. Next: mvn clean package")