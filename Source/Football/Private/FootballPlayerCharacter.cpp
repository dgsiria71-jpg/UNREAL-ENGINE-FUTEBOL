#include "FootballPlayerCharacter.h"

#include "FootballSimulationSubsystem.h"
#include "Net/UnrealNetwork.h"

AFootballPlayerCharacter::AFootballPlayerCharacter(const FObjectInitializer& ObjectInitializer)
    : Super(ObjectInitializer)
{
    bReplicates = true;
    SetReplicateMovement(false);
    if (GetCharacterMovement())
    {
        // Locomotion is resolved by the fixed football simulation. The
        // CharacterMovementComponent remains available for capsule/query use.
        GetCharacterMovement()->DisableMovement();
    }
}

void AFootballPlayerCharacter::GetLifetimeReplicatedProps(TArray<FLifetimeProperty>& OutLifetimeProps) const
{
    Super::GetLifetimeReplicatedProps(OutLifetimeProps);
    DOREPLIFETIME(AFootballPlayerCharacter, PlayerId);
    DOREPLIFETIME(AFootballPlayerCharacter, TeamId);
    DOREPLIFETIME(AFootballPlayerCharacter, bUserOwned);
}

void AFootballPlayerCharacter::SubmitInputIntent(const FFootballInputIntent& Intent)
{
    if (HasAuthority())
    {
        SubmitIntentToServerSimulation(Intent);
    }
    else
    {
        ServerSubmitInputIntent(Intent);
    }
}

void AFootballPlayerCharacter::ServerSubmitInputIntent_Implementation(const FFootballInputIntent& Intent)
{
    SubmitIntentToServerSimulation(Intent);
}

void AFootballPlayerCharacter::SubmitIntentToServerSimulation(const FFootballInputIntent& Intent)
{
    if (!HasAuthority() || PlayerId <= 0)
    {
        return;
    }

    UWorld* World = GetWorld();
    UFootballSimulationSubsystem* Simulation =
        World ? World->GetSubsystem<UFootballSimulationSubsystem>() : nullptr;
    if (!Simulation)
    {
        return;
    }

    LatestIntent = Intent;
    FFootballGameplayCommand Command;
    Command.SimulationTick = Simulation->GetSimulationTick() + 1;
    Command.OwnerPlayerId = PlayerId;
    Command.Intent = Intent;
    Simulation->SubmitGameplayCommand(Command);
}
