 0- 4: content_size: 0
 4- 8: id: 2 <GameSetupManager>
 8-12: content_size: 4
12-16: id: 32769 <PeerCount>
16-20: content: 268435456
20-24: leftover_bytes
...
13312-13316: content_size: 0
13316-13320: id: 15 <ActiveDLCs>

13320-13324: content_size: 8
13324-13328: id: 32770 <count> <--- This has to change - DONE
13328-13336: content: 72057594037927936

13336-13340: content_size: 4
13340-13344: id: 32782 <DLC> <--- This has to change - DONE
13344-13348: content: 3091269120
13348-13352: leftover_bytes

...
13320-13324: content_size: 0
13324-13328: id: 0

54 => 0x36
42 => 0x2a

15528-15532: elements_count: 54
15532-15640: elements_ids: [42, 2, 48, 43, 25, 7, 3, 21, 9, 50, 4, 5, 51, 6, 52, 40, 8, 54, 10, 33, 16, 11, 12, 13, 44, 28, 23, 14, 36, 15, 17, 18, 32, 19, 47, 20, 49, 27, 22, 24, 26, 46, 29, 30, 31, 34, 35, 37, 38, 39, 41, 45, 53, 55]
15640-16660: elements_names: ['SecondParties', 'GameSetupManager', 'SetupVictoryConditionIncome', 'Participant', 'SetupOptionalQuestFrequency', 'ParticipantType', 'Peers', 'SetupHostileTakeover', 'AccountUnlocks', 'SetupVictoryConditionDiplomacy', 'Peer', 'Values', 'SetupMapType', 'Available', 'SetupSkyscraperMaintenance', 'ThirdParties', 'Human', 'AdditionalVictoryConditions', 'Team', 'SetupStartSession', 'ActiveMods', 'value', 'CompanyColor', 'Maps', 'SetupVictoryConditionMonuments', 'SetupRawMaterial', 'SetupIncidents', 'GameSetupDifficulty', 'SetupStartShips', 'ActiveDLCs', 'ActiveLocalMods', 'SetupConstructionCostRefund', 'SetupStartCredits', 'SetupDistributionWorkforce', 'SetupVictoryConditionWealth', 'SetupFertility', 'SetupVictoryConditionAllOrOne', 'SetupOptionalQuestTimeout', 'SetupInactiveCosts', 'SetupLossCondition', 'SetupOptionalQuestRewards', 'SetupVictoryConditionPopulation', 'SetupRelocateBuildings', 'SetupRevealedMap', 'SetupRevenue', 'SetupStartSessionIslandDifficulty', 'SetupStartSessionIslandSize', 'SetupStartWithKontor', 'SetupTraderRefillRate', 'SetupInfluence', 'Difficulty', 'SetupVictoryConditionInvestors', 'SetupLoseConditionIslandHealth', 'SelectedDifficultyPreset']

16664-16668: attributes_count: 15 <--- This has to change
16668-16698: attributes_ids: 
[32776, 32769, 32770, 32771, 32772, 32773, 32774, 32775, 32777, 32778, 32779, 32780, 32781, 32782, 32783] 
[32776, 32769, 32770, 32771, 32772, 32773, 32774, 32775, 32777, 32778, 32779, 32780, 32781, 32782, 32783, 32784]<--- This has to change
16698-16870: attributes_names: 
['id', 'PeerCount', 'count', 'CompanyName', 'AccountId', 'CompanyPortraitGuid', 'CompanyLogoGuid', 'Asset', 'Coop', 'PlayerPossessions', 'GameSeed', 'Customizable', 'SavegameFolderW', 'ActiveHappyDayEvents', 'Profile']
['id', 'PeerCount', 'count', 'CompanyName', 'AccountId', 'CompanyPortraitGuid', 'CompanyLogoGuid', 'Asset', 'Coop', 'PlayerPossessions', 'GameSeed', 'Customizable', 'SavegameFolderW', 'DLC', 'ActiveHappyDayEvents', 'Profile']
 <--- This has to change

16880-16884+32: elements_ptr: 15528 <--- This has to change - DONE
16884-16888+32: attributes_ptr: 16664 <--- This has to change - DONE

16896+40


    "32769": "PeerCount",
    "32770": "count",
    "32771": "CompanyName",
    "32772": "AccountId",
    "32773": "CompanyPortraitGuid",
    "32774": "CompanyLogoGuid",
    "32775": "Asset",
    "32776": "id",
    "32777": "Coop",
    "32778": "PlayerPossessions",
    "32779": "GameSeed",
    "32780": "Customizable",
    "32781": "SavegameFolderW",
    "32782": "ActiveHappyDayEvents",
    "32783": "Profile"

    "32769": "PeerCount",
    "32770": "count",
    "32771": "CompanyName",
    "32772": "AccountId",
    "32773": "CompanyPortraitGuid",
    "32774": "CompanyLogoGuid",
    "32775": "Asset",
    "32776": "id",
    "32777": "Coop",
    "32778": "PlayerPossessions",
    "32779": "GameSeed",
    "32780": "Customizable",
    "32781": "SavegameFolderW",
    "32782": "DLC",
    "32783": "ActiveHappyDayEvents",
    "32784": "Profile"