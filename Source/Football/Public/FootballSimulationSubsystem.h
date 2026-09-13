#pragma once

#include "CoreMinimal.h"
#include "Subsystems/WorldSubsystem.h"
#include "FootballNormalizedContracts.h"
#include "FootballInputContracts.h"
#include "FootballSimulationSubsystem.generated.h"

/*
 * The subsystem is the Unreal adapter boundary. Recovery and fixed-point
 * reference code stay engine-independent; this layer owns tick scheduling,
 * authority checks, and later replication integration.
 */
UCLASS()
class FOOTBALL_API UFootballSimulationSubsystem : public UTickableWorldSubsystem
{
    GENERATED_BODY()

public:
    virtual void Initialize(FSubsystemCollectionBase& Collection) override;
    virtual void Deinitialize() override;
    virtual void Tick(float DeltaTime) override;
    virtual TStatId GetStatId() const override;
    virtual bool IsTickable() const override { return true; }

    UPROPERTY(EditAnywhere, Config, BlueprintReadOnly, Category="Simulation")
    float FixedStepSeconds = 1.0f / 120.0f;

    UFUNCTION(BlueprintCallable, Category="Simulation")
    bool SubmitGameplayCommand(const FFootballGameplayCommand& Command);

    UFUNCTION(BlueprintCallable, Category="Simulation")
    bool SubmitAuthoritativeBallContact(const FFootballBallContact& Contact);

    UFUNCTION(BlueprintPure, Category="Simulation")
    int64 GetSimulationTick() const { return SimulationTick; }

    UFUNCTION(BlueprintPure, Category="Simulation")
    FFootballBallState GetBallState() const { return BallState; }

private:
    void StepSimulation();

    float AccumulatorSeconds = 0.0f;
    int64 SimulationTick = 0;
    FFootballBallState BallState;
    TArray<FFootballGameplayCommand> PendingCommands;
    TArray<FFootballBallContact> PendingContacts;
};
