#include "FootballBallActor.h"
#include "Net/UnrealNetwork.h"

AFootballBallActor::AFootballBallActor()
{
    bReplicates = true;
    SetReplicateMovement(false);
    PrimaryActorTick.bCanEverTick = false;
}

bool AFootballBallActor::SetAuthoritativeState(const FFootballBallState& NewState)
{
    if (!HasAuthority())
    {
        return false;
    }

    AuthoritativeState = NewState;
    return true;
}

void AFootballBallActor::OnRep_AuthoritativeState()
{
    // Presentation components interpolate this snapshot; clients never solve it.
}

void AFootballBallActor::GetLifetimeReplicatedProps(
    TArray<FLifetimeProperty>& OutLifetimeProps) const
{
    Super::GetLifetimeReplicatedProps(OutLifetimeProps);
    DOREPLIFETIME(AFootballBallActor, AuthoritativeState);
}
