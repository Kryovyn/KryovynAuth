package tech.kryovyn.auth;
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
