# Examples

Each section pairs a **Bad** and a **Good** version of the title or of one body section. All examples describe one change: a settings form that silently dropped the user's time zone on save.

## Title

**Bad** titles leave a reviewer scanning the PR list unable to tell what was wrong in the code. The symptom says what a user saw, the mechanism says how the fix works. **Good** names the cause, in the file the diff changes.

### Bad: symptom

```
Fix time zone not saving in settings
```

### Bad: mechanism

```
Send timezone field in settings PATCH payload
```

### Good: cause

```
Fix SettingsForm omitting timeZone from the update payload
```

## Summary

**Bad** opens with the solution and reports the work. **Good** leads with what goes wrong if this does not merge, alone in the first paragraph.

### Bad

```markdown
## Summary

This PR refactors `SettingsForm` to use the shared `buildPayload` helper and adds the `timeZone` field. It also updates the tests and fixes a lint warning.

## Testing

- 42 unit tests passed
- Manually checked the settings page
```

### Good

```markdown
## Summary

Users who change their time zone in Settings see a success toast, but the value is never saved, so reminders keep firing in the old zone. Fixes #318.

`SettingsForm` now sends `timeZone` with the other profile fields.

Existing users with a wrong stored zone are not migrated; that needs a separate backfill once we know how many are affected.
```

## Review focus

**Bad** lists the diff or treats automated review as approval. **Good** names the decisions a person must still make.

### Bad

```markdown
## Review focus

- All files under `src/settings/`
- Formatting
- CI is green, ready to merge
```

### Good

```markdown
## Review focus

- `src/settings/SettingsForm.tsx`: `timeZone` falls back to the browser zone when empty; confirm that is better than rejecting the save.
- `src/api/profile.ts`: the endpoint now accepts IANA names only; check that no mobile client still sends UTC offsets.
- `src/settings/__snapshots__/`: regenerated, safe to skim.
```

## Screenshots

**Bad** describes the visual change in words or leaves it out. **Good** shows it.

### Bad

```markdown
The time zone dropdown now shows the saved value after reload.
```

### Good

```markdown
## Screenshots

| Before | After |
| --- | --- |
| ![Reloaded settings show UTC](/uploads/…/before.png) | ![Reloaded settings show Europe/Warsaw](/uploads/…/after.png) |
```
