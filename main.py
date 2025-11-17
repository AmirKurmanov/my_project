def find(numbers):
    result = []
    nums = list([-5, 1, 12, 17, 0, 13, 8, 3, 8])

    for i in range(len(nums)):
        current = nums[i]
        min_diff = float('inf')
        correct = None

        for j in range(len(nums)):
            if i == j:
                continue

            diff = abs(current - nums[j])

            if diff < min_diff:
                min_diff = diff
                correct = nums[j]
            elif diff == min_diff and nums[j] < correct:
                correct = nums[j]

        result.append(correct)

    return result

numbers = [-5, 1, 12, 17, 0, 13, 8, 3, 8]
result = find(numbers)
print(result)
