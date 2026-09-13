using UnrealBuildTool;

public class FootballTarget : TargetRules
{
    public FootballTarget(TargetInfo Target) : base(Target)
    {
        Type = TargetType.Game;
        DefaultBuildSettings = BuildSettingsVersion.V5;
        ExtraModuleNames.Add("Football");
    }
}
