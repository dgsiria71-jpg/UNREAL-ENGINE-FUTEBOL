using UnrealBuildTool;

public class Football : ModuleRules
{
    public Football(ReadOnlyTargetRules Target) : base(Target)
    {
        PCHUsage = PCHUsageMode.UseExplicitOrSharedPCHs;

        PublicDependencyModuleNames.AddRange(new string[]
        {
            "Core",
            "CoreUObject",
            "Engine",
            "NetCore",
            "EnhancedInput",
            "GameplayTags",
            "PhysicsCore"
        });

        PrivateDependencyModuleNames.AddRange(new string[]
        {
            "AnimGraphRuntime",
            "CommonUI",
            "ControlRig",
            "IKRig",
            "PoseSearch",
            "Slate",
            "SlateCore",
            "UMG"
        });
    }
}
