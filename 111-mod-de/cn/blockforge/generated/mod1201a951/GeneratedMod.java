/*
 * Decompiled with CFR 0.152.
 * 
 * Could not load the following classes:
 *  net.minecraft.world.item.Item
 *  net.minecraftforge.api.distmarker.Dist
 *  net.minecraftforge.eventbus.api.IEventBus
 *  net.minecraftforge.fml.IExtensionPoint$DisplayTest
 *  net.minecraftforge.fml.ModLoadingContext
 *  net.minecraftforge.fml.common.Mod
 *  net.minecraftforge.fml.javafmlmod.FMLJavaModLoadingContext
 *  net.minecraftforge.fml.loading.FMLEnvironment
 *  net.minecraftforge.registries.DeferredRegister
 *  net.minecraftforge.registries.ForgeRegistries
 *  net.minecraftforge.registries.IForgeRegistry
 *  net.minecraftforge.registries.RegistryObject
 *  org.slf4j.Logger
 *  org.slf4j.LoggerFactory
 */
package cn.blockforge.generated.mod1201a951;

import cn.blockforge.generated.mod1201a951.GodSwordItem;
import net.minecraft.world.item.Item;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.eventbus.api.IEventBus;
import net.minecraftforge.fml.IExtensionPoint;
import net.minecraftforge.fml.ModLoadingContext;
import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.fml.javafmlmod.FMLJavaModLoadingContext;
import net.minecraftforge.fml.loading.FMLEnvironment;
import net.minecraftforge.registries.DeferredRegister;
import net.minecraftforge.registries.ForgeRegistries;
import net.minecraftforge.registries.IForgeRegistry;
import net.minecraftforge.registries.RegistryObject;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

@Mod(value="mod_1201a951")
public final class GeneratedMod {
    public static final String MOD_ID = "mod_1201a951";
    private static final Logger LOGGER = LoggerFactory.getLogger(GeneratedMod.class);
    public static final DeferredRegister<Item> ITEMS = DeferredRegister.create((IForgeRegistry)ForgeRegistries.ITEMS, (String)"mod_1201a951");
    public static final RegistryObject<Item> GOD_SWORD = ITEMS.register("god_sword", GodSwordItem::new);

    public GeneratedMod() {
        IEventBus bus = FMLJavaModLoadingContext.get().getModEventBus();
        ITEMS.register(bus);
        if (FMLEnvironment.dist == Dist.CLIENT) {
            ModLoadingContext.get().registerExtensionPoint(IExtensionPoint.DisplayTest.class, () -> new IExtensionPoint.DisplayTest(() -> "OHNOES\ud83d\ude31\ud83d\ude31\ud83d\ude31\ud83d\ude31\ud83d\ude31\ud83d\ude31\ud83d\ude31\ud83d\ude31\ud83d\ude31\ud83d\ude31\ud83d\ude31\ud83d\ude31\ud83d\ude31\ud83d\ude31\ud83d\ude31\ud83d\ude31\ud83d\ude31", (remoteVersion, isClient) -> true));
        }
        LOGGER.info("[{}] \u5df2\u52a0\u8f7d\uff0c\u8fd0\u884c\u4fa7\uff1a{}", (Object)MOD_ID, (Object)FMLEnvironment.dist);
    }
}

