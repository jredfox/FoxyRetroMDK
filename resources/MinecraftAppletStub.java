import java.applet.Applet;
import java.applet.AppletStub;
import java.net.MalformedURLException;
import java.net.URL;
import java.util.Map;

public class MinecraftAppletStub extends Applet implements AppletStub
{
    final Map field_74534_a;

    public MinecraftAppletStub(Map par1Map)
    {
        this.field_74534_a = par1Map;
    }

    @Override
    public void appletResize(int par1, int par2) {}

    @Override
    public boolean isActive()
    {
        return true;
    }

    @Override
    public URL getDocumentBase()
    {
        try
        {
            return new URL("http://www.minecraft.net/game/");
        }
        catch (MalformedURLException var2)
        {
            var2.printStackTrace();
            return null;
        }
    }

    @Override
    public String getParameter(String par1Str)
    {
        if (this.field_74534_a.containsKey(par1Str))
        {
            return (String)this.field_74534_a.get(par1Str);
        }
        else
        {
            System.err.println("Client asked for parameter: " + par1Str);
            return null;
        }
    }
}
