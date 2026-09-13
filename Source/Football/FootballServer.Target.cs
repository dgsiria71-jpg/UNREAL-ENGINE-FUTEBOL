using UnrealBuildTool;

public class FootballServerTarget : TargetRules
{
    public FootballServerTarget(TargetInfo Target) : base(Target)
    {
        Type = TargetType.Server;
        DefaultBuildSettings = BuildSettingsVersion.V5;
        ExtraModuleNames.Add("Football");
    }
}
