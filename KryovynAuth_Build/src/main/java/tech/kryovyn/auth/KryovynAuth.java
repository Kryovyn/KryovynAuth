package tech.kryovyn.auth;
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
