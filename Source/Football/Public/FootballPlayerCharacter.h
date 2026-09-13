#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Character.h"
#include "FootballInputContracts.h"
#include "FootballPlayerCharacter.generated.h"

UCLASS()
class FOOTBALL_API AFootballPlayerCharacter : public ACharacter
{
    GENERATED_BODY()

public:
    explicit AFootballPlayerCharacter(const FObjectInitializer& ObjectInitializer);

    virtual void GetLifetimeReplicatedProps(TArray<FLifetimeProperty>& OutLifetimeProps) const override;

    UPROPERTY(Replicated, EditAnywhere, BlueprintReadOnly, Category="Identity")
    int32 PlayerId = 0;

    UPROPERTY(Replicated, EditAnywhere, BlueprintReadOnly, Category="Identity")
    int32 TeamId = 0;

    UPROPERTY(Replicated, EditAnywhere, BlueprintReadOnly, Category="Ownership")
    bool bUserOwned = false;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Input")
    FFootballInputIntent LatestIntent;

    UFUNCTION(BlueprintCallable, Category="Input")
    void SubmitInputIntent(const FFootballInputIntent& Intent);

    UFUNCTION(Server, Reliable)
    void ServerSubmitInputIntent(const FFootballInputIntent& Intent);

private:
    void SubmitIntentToServerSimulation(const FFootballInputIntent& Intent);
};
