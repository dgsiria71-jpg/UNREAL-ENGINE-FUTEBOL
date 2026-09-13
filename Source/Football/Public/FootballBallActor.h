#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "FootballNormalizedContracts.h"
#include "FootballBallActor.generated.h"

UCLASS()
class FOOTBALL_API AFootballBallActor : public AActor
{
    GENERATED_BODY()

public:
    AFootballBallActor();

    UPROPERTY(ReplicatedUsing=OnRep_AuthoritativeState, BlueprintReadOnly, Category="Authority")
    FFootballBallState AuthoritativeState;

    UFUNCTION(BlueprintCallable, Category="Authority")
    bool SetAuthoritativeState(const FFootballBallState& NewState);

    UFUNCTION(BlueprintPure, Category="Authority")
    FFootballBallState GetAuthoritativeState() const { return AuthoritativeState; }

protected:
    UFUNCTION()
    void OnRep_AuthoritativeState();

    virtual void GetLifetimeReplicatedProps(
        TArray<FLifetimeProperty>& OutLifetimeProps) const override;
};
