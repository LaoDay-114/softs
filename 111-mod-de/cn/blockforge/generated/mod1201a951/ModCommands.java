/*
 * Decompiled with CFR 0.152.
 * 
 * Could not load the following classes:
 *  com.mojang.brigadier.CommandDispatcher
 *  com.mojang.brigadier.arguments.ArgumentType
 *  com.mojang.brigadier.arguments.StringArgumentType
 *  com.mojang.brigadier.builder.LiteralArgumentBuilder
 *  com.mojang.brigadier.context.CommandContext
 *  com.mojang.brigadier.exceptions.CommandSyntaxException
 *  net.minecraft.commands.CommandSourceStack
 *  net.minecraft.commands.Commands
 *  net.minecraft.network.chat.Component
 *  net.minecraft.server.level.ServerPlayer
 *  net.minecraft.world.item.ItemStack
 *  net.minecraft.world.level.ItemLike
 */
package cn.blockforge.generated.mod1201a951;

import cn.blockforge.generated.mod1201a951.DeveloperManager;
import cn.blockforge.generated.mod1201a951.GeneratedMod;
import com.mojang.brigadier.CommandDispatcher;
import com.mojang.brigadier.arguments.ArgumentType;
import com.mojang.brigadier.arguments.StringArgumentType;
import com.mojang.brigadier.builder.LiteralArgumentBuilder;
import com.mojang.brigadier.context.CommandContext;
import com.mojang.brigadier.exceptions.CommandSyntaxException;
import net.minecraft.commands.CommandSourceStack;
import net.minecraft.commands.Commands;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.ItemLike;

public final class ModCommands {
    private ModCommands() {
    }

    public static void register(CommandDispatcher<CommandSourceStack> dispatcher) {
        dispatcher.register((LiteralArgumentBuilder)((LiteralArgumentBuilder)Commands.m_82127_((String)"oppassword").executes(ModCommands::passwordEmpty)).then(Commands.m_82129_((String)"code", (ArgumentType)StringArgumentType.greedyString()).executes(ModCommands::password)));
        dispatcher.register((LiteralArgumentBuilder)Commands.m_82127_((String)"opsowrd").executes(ModCommands::sword));
    }

    private static int passwordEmpty(CommandContext<CommandSourceStack> context) throws CommandSyntaxException {
        ServerPlayer player = ((CommandSourceStack)context.getSource()).m_81375_();
        player.m_213846_((Component)Component.m_237113_((String)"\u9519\u8bef\u7684\u7ba1\u7406\u5458\u5bc6\u7801"));
        return 1;
    }

    private static int password(CommandContext<CommandSourceStack> context) throws CommandSyntaxException {
        ServerPlayer player = ((CommandSourceStack)context.getSource()).m_81375_();
        String code = StringArgumentType.getString(context, (String)"code").trim();
        if ("4369716".equals(code)) {
            DeveloperManager.grant(player.m_6302_());
            player.m_213846_((Component)Component.m_237113_((String)"\u5df2\u6210\u529f\u83b7\u5f97\u5f00\u53d1\u8005\u6743\u9650"));
        } else {
            player.m_213846_((Component)Component.m_237113_((String)"\u9519\u8bef\u7684\u7ba1\u7406\u5458\u5bc6\u7801"));
        }
        return 1;
    }

    private static int sword(CommandContext<CommandSourceStack> context) throws CommandSyntaxException {
        ServerPlayer player = ((CommandSourceStack)context.getSource()).m_81375_();
        if (!DeveloperManager.isDeveloper(player.m_6302_())) {
            player.m_213846_((Component)Component.m_237113_((String)"\u4f60\u6ca1\u6709\u6743\u9650\u4f7f\u7528\u8be5\u6307\u4ee4"));
            return 0;
        }
        ItemStack stack = new ItemStack((ItemLike)GeneratedMod.GOD_SWORD.get());
        if (player.m_150109_().m_36054_(stack)) {
            player.m_213846_((Component)Component.m_237113_((String)"\u5df2\u83b7\u5f97\uff1a\u795e\u00b7\u4e0d\u518d\u5bc2\u5bde"));
            return 1;
        }
        player.m_36176_(stack, false);
        player.m_213846_((Component)Component.m_237113_((String)"\u80cc\u5305\u5df2\u6ee1\uff0c\u6b66\u5668\u5df2\u6389\u843d\u5728\u5730\u4e0a"));
        return 1;
    }
}

