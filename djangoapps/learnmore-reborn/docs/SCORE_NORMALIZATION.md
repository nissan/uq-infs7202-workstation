# Quiz Score Normalization

Score normalization is a feature that allows instructors to standardize quiz question scores based on various statistical methods. This helps create more consistent grading across questions of different difficulty levels and improves the validity of assessment scores.

## Overview

The score normalization system provides several methods to adjust raw scores:

1. **Z-Score Normalization**: Standardizes scores based on mean and standard deviation
2. **Min-Max Scaling**: Transforms scores to fit within a specified range
3. **Percentile Ranking**: Adjusts scores based on historical performance data
4. **Custom Normalization**: Maps raw scores to custom values using a lookup table

## Configuration

Normalization is configured at the question level, enabling fine-grained control over how each question's score is adjusted.

### Normalization Methods

#### Z-Score Normalization

Z-score normalization standardizes scores around a mean with a specific standard deviation. This method ensures that scores follow a normal distribution.

Parameters:
- `mean`: The center point for normalized scores (default: points/2)
- `std_dev`: The standard deviation (default: points/6)

Formula: `normalized_score = (raw_score - mean) / std_dev * (points/4) + (points/2)`

#### Min-Max Scaling

Min-Max scaling transforms scores from one range to another, typically used to normalize scores to a specific range (e.g., 0-10 or 0-100).

Parameters:
- `input_min`: The minimum input score (default: 0)
- `input_max`: The maximum input score (default: points) 
- `output_min`: The minimum output score (default: 0)
- `output_max`: The maximum output score (default: points)

Formula: `normalized_score = output_min + ((raw_score - input_min) * (output_max - output_min) / (input_max - input_min))`

#### Percentile Ranking

Percentile ranking normalizes scores based on historical performance data, assigning scores based on where a student's performance falls relative to past attempts.

Parameters:
- `percentiles`: A mapping of percentile scores to normalized values

Example mapping:
```json
{
  "10": 1,
  "20": 2,
  "30": 3,
  "40": 4,
  "50": 5,
  "60": 6,
  "70": 7,
  "80": 8,
  "90": 9,
  "100": 10
}
```

#### Custom Normalization

Custom normalization allows mapping specific raw scores to predefined normalized values, providing complete control over the score transformation.

Parameters:
- `mapping`: A dictionary mapping from raw scores to normalized scores

Example mapping:
```json
{
  "1": 3,
  "2": 4,
  "3": 5,
  "4": 6,
  "5": 7,
  "6": 8,
  "7": 9,
  "8": 9,
  "9": 10
}
```

## Implementation Details

Score normalization is implemented in the `normalize_score()` method of the `MultipleChoiceQuestion` model. When a question has a normalization method other than "none", the method automatically transforms the calculated raw points to a normalized score before returning the result.

```python
def normalize_score(self, points_earned):
    """Normalize the score based on the selected normalization method."""
    # If no points or maximum points, normalization isn't needed
    if points_earned == 0 or points_earned == self.points:
        return points_earned
        
    # Get parameters with defaults if not specified
    params = self.normalization_parameters
    
    if self.normalization_method == 'zscore':
        # Z-score normalization implementation
        mean = params.get('mean', self.points / 2)
        std_dev = params.get('std_dev', self.points / 6)
        
        if std_dev == 0:  # Avoid division by zero
            std_dev = 1
            
        z_score = (points_earned - mean) / std_dev
        normalized = int(round((z_score * (self.points / 4)) + (self.points / 2)))
    
    elif self.normalization_method == 'minmax':
        # Min-Max scaling implementation
        output_min = params.get('output_min', 0)
        output_max = params.get('output_max', self.points)
        input_min = params.get('input_min', 0)
        input_max = params.get('input_max', self.points)
        
        normalized = output_min + ((points_earned - input_min) * 
                                  (output_max - output_min) / 
                                  (input_max - input_min))
        normalized = int(round(normalized))
    
    # Other methods implementation...
    
    # Ensure normalized score is within bounds
    normalized = max(0, min(normalized, self.points))
    return normalized
```

## Best Practices

### When to Use Normalization

Score normalization is most useful in these scenarios:

1. **Varying difficulty levels**: When some questions are consistently more difficult than others
2. **Mixed question types**: When combining different question types in a single assessment
3. **Comparative assessments**: When comparing scores across different quiz sections or timeframes
4. **Grading on a curve**: When you want to ensure a specific distribution of scores
5. **Standardizing scores**: When aggregating scores from different assessors or questions

### Choosing the Right Method

- **Z-score normalization**: Best for ensuring a normal distribution of scores
- **Min-Max scaling**: Best for transforming scores to a specific range
- **Percentile ranking**: Best for maintaining consistent meaning across different quiz versions
- **Custom normalization**: Best for specialized grading policies or curves

### Additional Considerations

- Score normalization should be used cautiously, as it alters the direct relationship between performance and score
- Always explain the normalization method to students if using it for high-stakes assessments
- Test normalization methods with sample data before applying them to actual assessments
- Consider the educational goals of the assessment when selecting a normalization method
- Monitor the impact of normalization on student performance and motivation

## Related Features

- **Partial credit scoring**: Works in conjunction with normalization
- **Question analytics**: Provides data that can inform normalization parameters
- **Weighted questions**: Can be used alongside normalization for further score adjustment
- **Instructor analytics**: Helps evaluate the effectiveness of normalization methods