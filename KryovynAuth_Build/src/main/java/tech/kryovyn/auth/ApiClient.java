package tech.kryovyn.auth;
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
