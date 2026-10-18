package tech.kryovyn.auth;
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
