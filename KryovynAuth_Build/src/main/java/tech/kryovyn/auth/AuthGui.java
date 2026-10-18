package tech.kryovyn.auth;
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
