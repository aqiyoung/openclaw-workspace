---
name: "openclaw-native-string-i18n"
description: "OpenClaw i18n edits: nativeString hash + 3-file sync, server-sent error translations, gateway UI string i18n."
---

# OpenClaw nativeString / i18n edits

Use when adding, translating, or i18n-izing user-visible strings in the OpenClaw Android app or the gateway's error/UI messages. Pick the path that matches your starting state.

---

## Path A — Add or translate a `nativeString()` entry in Kotlin

When a hardcoded Chinese string exists in Kotlin source, OR you need a new English source string and the generator cannot run (no `node_modules`, translator unavailable).

### Architecture (4 files must stay consistent)
1. **Kotlin code** — `nativeString("English source text")`
2. **`NativeStringResources.kt`** — `"English" to R.string.native_<16hex>` at `apps/android/app/src/main/java/ai/openclaw/app/i18n/NativeStringResources.kt`
3. **`values/strings.xml`** — English resource
4. **`values-zh-rCN/strings.xml`** — Chinese resource

### Steps
1. **Compute the resource hash.**
   ```bash
   node -e "const c=require('crypto');const id=['android','<RELATIVE_FILE_PATH>','<SOURCE_STRING>'].join('\\u0000');console.log('native.'+c.createHash('sha256').update(id).digest('hex').slice(0,16));"
   ```
   - XML name = `native_<16hex>`; Kotlin ref = `R.string.native_<16hex>`

2. **Edit the Kotlin source.** Replace hardcoded Chinese with `nativeString("English source text")`. Interpolation: `nativeString("English $thing", thing)`. In composables use `nativeString()`.

3. **Edit `NativeStringResources.kt`.** Add an alphabetically-sorted entry:
   ```kotlin
   "English source text" to R.string.native_<16hex>,
   ```

4. **Edit `values/strings.xml`.** Add before `</resources>`:
   ```xml
   <string name="native_<16hex>" formatted="false" tools:ignore="Typos,TypographyDashes,TypographyEllipsis">"English source text"</string>
   ```

5. **Edit `values-zh-rCN/strings.xml`.** Add the same ID with the Chinese translation.

### Verification
- `grep native_<16hex>` hits all 3 i18n files; all use the same hash ID
- `grep -n '"[一-龥]' <kotlin-file>` returns nothing

### Pitfalls
- Hash depends on the exact file path AND exact source string.
- Do not touch `nativeStringResourceIds` (auto-generated).
- `formatted="false"` required when the source contains `$`.
- `native-source.json` only needs updating if the workflow runs `native:i18n:check` (build-android.yml does not).

---

## Path B — Translate a server-sent error shown verbatim in the Android app

When the user reports an English error string in the Android app, but grepping the repo returns nothing. The Gateway sends these raw; the app displays them via `userFacingChatError` in `ChatScreen.kt` (`else -> error` fallback).

### Steps
1. Grep the phrase. If absent, treat as server-generated.
2. Add a pattern branch in `userFacingChatError` (input is lowercased):
   ```kotlin
   lower.contains("agent run failed") || lower.contains("failed before producing") -> nativeString("中文翻译")
   ```
3. Translate the replacement string through Path A (compute its hash from the ChatScreen.kt path + chosen English source, then sync the 3 i18n files).
4. Only add branches for stable, recurring server messages.

### Verification
- `grep native_<16hex>` hits all 3 i18n files
- New branch sits above the `else -> error` fallback

---

## Path C — i18n-ize a gateway error/UI string in TypeScript source

When the English message originates from `.ts` source in the repo (not a server-sent error).

### Steps
1. **Locate in installed dist.**
   ```bash
   grep -rn "exact message text" ~/.nvm/versions/node/*/lib/node_modules/openclaw/dist/ --include="*.js" 2>/dev/null
   ```
2. **Clone source**:
   ```bash
   cd /tmp && rm -rf openclaw-src && git clone --depth 1 git@github.com:aqiyoung/openclaw.git openclaw-src
   ```
3. **Find the `.ts` source.** Grep `src/` for the string or a nearby constant.
4. **Edit the string.** Concise, matching tone. Preserve `${...}`. Replace the full exact string including punctuation — never a substring.
5. **Update every test assertion**:
   ```bash
   grep -rn "old english string" /tmp/openclaw-src/src/ --include="*.ts" 2>/dev/null
   ```
6. **Verify no residual English**:
   ```bash
   grep -rn "old english string" /tmp/openclaw-src/src/ --include="*.ts" 2>/dev/null || echo "✅ clean"
   ```
7. **Commit and push**:
   ```bash
   cd /tmp/openclaw-src && git add -A && git commit -m "i18n: 汉化 <description>" && git push origin main --force
   ```

### Pitfalls
- Takes effect only after gateway restart or APK rebuild.
- Do not translate debug strings, user config values, or third-party messages.
- Substring sed replacements produce mixed-language fragments.

---

## Commit & release (all paths)
Push main and retag (delete + recreate) to trigger the CI tag-bump Android build.
```bash
git tag -d <tag> && git push origin :refs/tags/<tag>
git tag <tag> && git push origin <tag>
```
