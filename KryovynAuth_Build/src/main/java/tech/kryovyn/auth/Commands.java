package tech.kryovyn.auth;
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
            for(String line:m.split("\n"))p.sendMessage(Utils.color(line));
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
