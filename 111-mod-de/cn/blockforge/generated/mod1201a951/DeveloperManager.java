/*
 * Decompiled with CFR 0.152.
 */
package cn.blockforge.generated.mod1201a951;

import java.util.Locale;
import java.util.Set;
import java.util.concurrent.ConcurrentHashMap;

public final class DeveloperManager {
    public static final String DEFAULT_DEVELOPER = "xiaomao";
    public static final String CORRECT_PASSWORD = "4369716";
    private static final Set<String> DEVELOPERS = ConcurrentHashMap.newKeySet();

    private DeveloperManager() {
    }

    public static boolean isDeveloper(String playerName) {
        String key = DeveloperManager.normalize(playerName);
        return key != null && DEVELOPERS.contains(key);
    }

    public static void grant(String playerName) {
        String key = DeveloperManager.normalize(playerName);
        if (key != null) {
            DEVELOPERS.add(key);
        }
    }

    private static String normalize(String name) {
        return name == null ? null : name.trim().toLowerCase(Locale.ROOT);
    }

    static {
        DEVELOPERS.add(DeveloperManager.normalize(DEFAULT_DEVELOPER));
    }
}

