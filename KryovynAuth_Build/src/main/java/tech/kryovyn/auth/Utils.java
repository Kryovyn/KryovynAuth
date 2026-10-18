package tech.kryovyn.auth;
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
