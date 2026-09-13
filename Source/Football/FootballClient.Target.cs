using UnrealBuildTool;

public class FootballClientTarget : TargetRules
{
    public FootballClientTarget(TargetInfo Target) : base(Target)
    {
        Type = TargetType.Client;
        DefaultBuildSettings = BuildSettingsVersion.V5;
        ExtraModuleNames.Add("Football");
    }
}
