/*
 * Decompiled with CFR 0.152.
 * 
 * Could not load the following classes:
 *  javax.annotation.Nullable
 *  net.minecraft.network.chat.Component
 *  net.minecraft.network.chat.MutableComponent
 *  net.minecraft.network.chat.TextColor
 *  net.minecraft.server.level.ServerLevel
 *  net.minecraft.server.level.ServerPlayer
 *  net.minecraft.world.entity.Entity
 *  net.minecraft.world.entity.EntityType
 *  net.minecraft.world.entity.EquipmentSlot
 *  net.minecraft.world.entity.EquipmentSlot$Type
 *  net.minecraft.world.entity.LightningBolt
 *  net.minecraft.world.entity.LivingEntity
 *  net.minecraft.world.entity.player.Player
 *  net.minecraft.world.item.Item$Properties
 *  net.minecraft.world.item.ItemStack
 *  net.minecraft.world.item.SwordItem
 *  net.minecraft.world.item.Tier
 *  net.minecraft.world.item.TooltipFlag
 *  net.minecraft.world.item.crafting.Ingredient
 *  net.minecraft.world.level.Level
 */
package cn.blockforge.generated.mod1201a951;

import java.util.List;
import javax.annotation.Nullable;
import net.minecraft.network.chat.Component;
import net.minecraft.network.chat.MutableComponent;
import net.minecraft.network.chat.TextColor;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.EquipmentSlot;
import net.minecraft.world.entity.LightningBolt;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.SwordItem;
import net.minecraft.world.item.Tier;
import net.minecraft.world.item.TooltipFlag;
import net.minecraft.world.item.crafting.Ingredient;
import net.minecraft.world.level.Level;

public final class GodSwordItem
extends SwordItem {
    private static final int GRADIENT_START = 16738740;
    private static final int GRADIENT_END = 0xFF0000;

    public GodSwordItem() {
        super((Tier)new GodTier(), 100000, 100000.0f, new Item.Properties().m_41487_(1));
    }

    public Component m_7626_(ItemStack stack) {
        return GodSwordItem.gradient("\u795e\u00b7\u4e0d\u518d\u5bc2\u5bde");
    }

    public void m_7373_(ItemStack stack, @Nullable Level level, List<Component> tooltip, TooltipFlag flag) {
        tooltip.add(GodSwordItem.gradient("\u4f24\u5bb3\uff1a\u65e0\u9650"));
        tooltip.add(GodSwordItem.gradient("\u653b\u51fb\u901f\u5ea6\uff1a\u65e0\u9650"));
        tooltip.add(GodSwordItem.gradient("\u8e22\u51fa\u6e38\u620f\uff08\u5bf9\u4e8e\u73a9\u5bb6\uff09"));
        tooltip.add(GodSwordItem.gradient("\u542f\u7528\u76ee\u6807\u6b7b\u4ea1\u4e8b\u4ef6\uff08setdeah\uff09"));
        tooltip.add(GodSwordItem.gradient("\u6e05\u9664\u76ee\u6807\u7684\u6240\u6709\u7269\u54c1\uff0c\u76d4\u7532\uff0c\u672b\u5f71\u7bb1\u5b58\u50a8\u7684\u7269\u54c1\uff08\u5bf9\u4e8e\u73a9\u5bb6\uff09"));
        tooltip.add(GodSwordItem.gradient("\u5f3a\u5236\u4f7f\u76ee\u6807\u6d88\u5931"));
    }

    public boolean onLeftClickEntity(ItemStack stack, Player player, Entity entity) {
        if (entity instanceof LivingEntity) {
            LivingEntity target = (LivingEntity)entity;
            if (!player.m_9236_().m_5776_()) {
                this.unleash(player, target);
                return true;
            }
        }
        return false;
    }

    public boolean m_7579_(ItemStack stack, LivingEntity target, LivingEntity attacker) {
        if (attacker instanceof Player) {
            Player player = (Player)attacker;
            if (!target.m_9236_().m_5776_()) {
                this.unleash(player, target);
            }
        }
        return true;
    }

    private void unleash(Player attacker, LivingEntity target) {
        ServerLevel serverLevel;
        LightningBolt bolt;
        if (target.m_21224_()) {
            return;
        }
        Level level = target.m_9236_();
        if (level instanceof ServerLevel && (bolt = (LightningBolt)EntityType.f_20465_.m_20615_((Level)(serverLevel = (ServerLevel)level))) != null) {
            bolt.m_6027_(target.m_20185_(), target.m_20186_(), target.m_20189_());
            if (attacker instanceof ServerPlayer) {
                ServerPlayer sp = (ServerPlayer)attacker;
                bolt.m_20879_(sp);
            }
            bolt.m_20874_(false);
            serverLevel.m_7967_((Entity)bolt);
        }
        for (ServerLevel slot : EquipmentSlot.values()) {
            if (slot.m_20743_() != EquipmentSlot.Type.ARMOR) continue;
            target.m_8061_((EquipmentSlot)slot, ItemStack.f_41583_);
        }
        target.m_6469_(target.m_269291_().m_269264_(), target.m_21233_() * 10.0f);
        target.m_21153_(0.0f);
        target.m_6074_();
        if (target instanceof Player) {
            Player victim = (Player)target;
            victim.m_150109_().m_6211_();
            victim.m_36327_().m_6211_();
            if (victim instanceof ServerPlayer) {
                ServerPlayer serverVictim = (ServerPlayer)victim;
                if (serverVictim.f_8906_ != null) {
                    serverVictim.f_8906_.m_9942_((Component)Component.m_237113_((String)"\u4f60\u5df2\u88ab\u6b64\u670d\u52a1\u5668\u5c01\u79811s"));
                }
            }
        }
    }

    private static Component gradient(String text) {
        MutableComponent result = Component.m_237119_();
        int len = text.length();
        if (len == 0) {
            return result;
        }
        for (int i = 0; i < len; ++i) {
            float t = (float)i / (float)(len - 1);
            int r = (int)(255.0f + t * 0.0f);
            int g = (int)(105.0f + t * -105.0f);
            int b = (int)(180.0f + t * -180.0f);
            int rgb = r << 16 | g << 8 | b;
            TextColor color = TextColor.m_131266_((int)rgb);
            result.m_7220_((Component)Component.m_237113_((String)String.valueOf(text.charAt(i))).m_130938_(style -> style.m_131148_(color)));
        }
        return result;
    }

    private static final class GodTier
    implements Tier {
        private GodTier() {
        }

        public int m_6609_() {
            return Integer.MAX_VALUE;
        }

        public float m_6624_() {
            return 100.0f;
        }

        public float m_6631_() {
            return 100000.0f;
        }

        public int m_6604_() {
            return 4;
        }

        public int m_6601_() {
            return 15;
        }

        public Ingredient m_6282_() {
            return Ingredient.f_43901_;
        }
    }
}

